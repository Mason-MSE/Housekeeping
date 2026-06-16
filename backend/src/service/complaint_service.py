"""Business logic for service-order complaints, refunds, and payment waivers."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.complaint import ComplaintEvidenceModel, ComplaintModel
from model.service_order import ServiceOrderModel
from model.user import UserModel
from model.wallet import TransactionModel, WalletModel
from schemas.complaint import (
    ComplaintAdminDetailOutSchema,
    ComplaintCreateSchema,
    ComplaintEvidenceSchema,
    ComplaintOutSchema,
    ComplaintResolveSchema,
)
from service.in_app_notify import notify_user
from service.order_payment_amount import resolve_guest_order_pay_amount
from service.portal_service import PortalService


COMPLAINT_WINDOW_DAYS = 15


def _mysql_errno(exc: SQLAlchemyError) -> Optional[int]:
    """Return pymysql / MySQL driver errno from a SQLAlchemy DBAPI error, if present."""
    orig_obj = getattr(exc, 'orig', None)
    if orig_obj is not None and getattr(orig_obj, 'args', None):
        if len(orig_obj.args) >= 1 and isinstance(orig_obj.args[0], int):
            return orig_obj.args[0]
    return None


def _error_mentions_complaint_table(msg_lower: str) -> bool:
    """True if MySQL error likely refers to complaint / complaint_evidence (not other tables)."""
    if 'complaint_evidence' in msg_lower:
        return True
    # db.table form, or quoted table name
    if '.complaint' in msg_lower or '`complaint`' in msg_lower or "'complaint'" in msg_lower:
        return True
    return False


class ComplaintService:
    """Create and resolve complaints tied to service orders."""

    def __init__(self, db: Session) -> None:
        """Initialize the complaint service with a database session."""
        self.db = db

    def _get_order(self, order_id: int) -> Optional[ServiceOrderModel]:
        """Fetch a non-deleted service order by its ID."""
        return self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.order_id == order_id,
            ServiceOrderModel.is_deleted == 0,
        ).first()

    def _paid_amount(self, order_id: int, guest_id: int) -> Decimal:
        """Return the total completed payment amount for an order by a guest."""
        row = (
            self.db.query(TransactionModel)
            .filter(
                TransactionModel.order_id == order_id,
                TransactionModel.user_id == guest_id,
                TransactionModel.type == 'payment',
                TransactionModel.status == 'completed',
                TransactionModel.is_deleted == 0,
            )
            .order_by(TransactionModel.create_time.desc())
            .first()
        )
        if row is None or row.amount is None:
            return Decimal('0')
        return Decimal(str(row.amount))

    def _cleaner_income_total(self, order_id: int, cleaner_id: int) -> Decimal:
        """Return the total completed income transactions for a cleaner on an order."""
        rows = (
            self.db.query(TransactionModel)
            .filter(
                TransactionModel.order_id == order_id,
                TransactionModel.user_id == cleaner_id,
                TransactionModel.type == 'income',
                TransactionModel.status == 'completed',
                TransactionModel.is_deleted == 0,
            )
            .all()
        )
        total = Decimal('0')
        for row in rows:
            if row.amount is not None:
                total += Decimal(str(row.amount))
        return total

    def _pending_payment_row(
        self, order_id: int, guest_id: int
    ) -> Optional[TransactionModel]:
        """Fetch the pending payment transaction for an order by a guest."""
        return (
            self.db.query(TransactionModel)
            .filter(
                TransactionModel.order_id == order_id,
                TransactionModel.user_id == guest_id,
                TransactionModel.type == 'payment',
                TransactionModel.status == 'pending',
                TransactionModel.is_deleted == 0,
            )
            .first()
        )

    def _validate_eligibility(self, order: ServiceOrderModel, guest_id: int) -> None:
        """Raise HTTPException if the order is not eligible for a complaint."""
        if order.guest_id != guest_id:
            raise HTTPException(status_code=403, detail='This order does not belong to you')
        if order.actual_complete is None:
            raise HTTPException(status_code=400, detail='Order is not finished yet')
        now = datetime.utcnow()
        if order.actual_complete > now:
            raise HTTPException(status_code=400, detail='Invalid completion time on order')
        if now - order.actual_complete > timedelta(days=COMPLAINT_WINDOW_DAYS):
            raise HTTPException(
                status_code=400,
                detail=f'Complaints must be filed within {COMPLAINT_WINDOW_DAYS} days after service completion',
            )
        if order.status == 8:
            raise HTTPException(status_code=400, detail='Cancelled orders cannot be disputed')

    def _existing_complaint_for_order(self, order_id: int) -> Optional[ComplaintModel]:
        """Return the first non-deleted complaint for the given order, if any."""
        return (
            self.db.query(ComplaintModel)
            .filter(
                ComplaintModel.order_id == order_id,
                ComplaintModel.is_deleted == 0,
            )
            .first()
        )

    def create_complaint(self, guest_id: int, payload: ComplaintCreateSchema) -> ComplaintOutSchema:
        """Create a complaint with optional evidence URLs (e.g. base64 data URLs)."""
        try:
            order = self._get_order(payload.order_id)
            if not order:
                raise HTTPException(status_code=404, detail='Order not found')
            self._validate_eligibility(order, guest_id)
            if self._existing_complaint_for_order(order.order_id):
                raise HTTPException(status_code=400, detail='A complaint already exists for this order')

            complaint = ComplaintModel(
                order_id=order.order_id,
                guest_id=guest_id,
                title=payload.title.strip(),
                description=(payload.description or '').strip() or None,
                status='pending',
            )
            self.db.add(complaint)
            self.db.flush()

            order_no_for_notify = order.order_no

            for idx, url in enumerate(payload.evidence_urls[:20]):
                if not url or not str(url).strip():
                    continue
                self.db.add(
                    ComplaintEvidenceModel(
                        complaint_id=complaint.id,
                        photo_url=str(url).strip()[:500000],
                        sort_order=idx,
                    )
                )

            self.db.flush()
            result = self._to_out(complaint, include_evidence=True)
            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as exc:
            self.db.rollback()
            orig = str(getattr(exc, 'orig', exc) or exc)
            lower = orig.lower()
            errno = _mysql_errno(exc)
            missing_table = (
                "doesn't exist" in lower
                or 'unknown table' in lower
                or errno == 1146
            )
            if missing_table and _error_mentions_complaint_table(lower):
                raise HTTPException(
                    status_code=503,
                    detail=(
                        'MySQL cannot find tables `complaint` or `complaint_evidence` in the database '
                        'configured as DB_NAME (this is separate from `notification`). '
                        'Restart the backend once: startup runs ensure_complaint_tables() to create them. '
                        'Or run: cd backend/src && python run_complaint_migration.py. '
                        f'Raw error: {orig[:400]}'
                    ),
                ) from exc
            if '1406' in orig or 'data too long' in lower:
                raise HTTPException(
                    status_code=400,
                    detail='Evidence image is too large. Use smaller images or fewer attachments.',
                ) from exc
            raise HTTPException(
                status_code=503,
                detail=(
                    'Could not save the complaint. Check the MySQL message below '
                    '(e.g. unknown column, access denied, wrong database). '
                    f'Detail: {orig[:700]}'
                ),
            ) from exc

        try:
            notify_user(
                self.db,
                guest_id,
                'Complaint submitted',
                f'Your complaint for order {order_no_for_notify} was received. We will review it shortly.',
                'info',
                '/my-orders',
            )
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()

        return result

    def list_my_complaints(self, guest_id: int) -> List[ComplaintOutSchema]:
        """List complaints filed by the guest."""
        """List complaints filed by the guest."""
        try:
            rows = (
                self.db.query(ComplaintModel)
                .filter(
                    ComplaintModel.guest_id == guest_id,
                    ComplaintModel.is_deleted == 0,
                )
                .order_by(ComplaintModel.create_time.desc())
                .all()
            )
        except SQLAlchemyError:
            return []
        return [self._to_out(r, include_evidence=True) for r in rows]

    def list_admin(
        self,
        status: Optional[str],
        page: int,
        page_size: int,
    ) -> Tuple[List[ComplaintOutSchema], int]:
        """Paginated list for admins."""
        query = self.db.query(ComplaintModel).filter(ComplaintModel.is_deleted == 0)
        if status:
            query = query.filter(ComplaintModel.status == status)
        total = query.count()
        offset = max(page - 1, 0) * page_size
        rows = (
            query.order_by(ComplaintModel.create_time.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return [self._to_out(r, include_evidence=True) for r in rows], total

    def get_one(self, complaint_id: int) -> ComplaintAdminDetailOutSchema:
        """Fetch a single complaint with full detail including booking info."""
        row = (
            self.db.query(ComplaintModel)
            .filter(
                ComplaintModel.id == complaint_id,
                ComplaintModel.is_deleted == 0,
            )
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail='Complaint not found')
        base = self._to_out(row, include_evidence=True)
        portal = PortalService(self.db)
        booking = portal.get_order_detail(row.order_id, row.guest_id)
        payload = base.model_dump()
        payload['booking_detail'] = booking
        return ComplaintAdminDetailOutSchema(**payload)

    def resolve_complaint(
        self,
        complaint_id: int,
        admin_user_id: int,
        payload: ComplaintResolveSchema,
    ) -> ComplaintOutSchema:
        """Apply admin resolution: reject, refund, or waive part of unpaid balance."""
        complaint = (
            self.db.query(ComplaintModel)
            .filter(
                ComplaintModel.id == complaint_id,
                ComplaintModel.is_deleted == 0,
            )
            .first()
        )
        if not complaint:
            raise HTTPException(status_code=404, detail='Complaint not found')
        if complaint.status != 'pending':
            raise HTTPException(status_code=400, detail='Complaint is already processed')

        order = self._get_order(complaint.order_id)
        if not order:
            raise HTTPException(status_code=404, detail='Order not found')

        action = (payload.action or '').strip().lower()
        paid = self._paid_amount(order.order_id, complaint.guest_id)
        is_paid = paid > Decimal('0')

        if action == 'reject':
            complaint.status = 'rejected'
            complaint.resolution_type = 'reject'
            complaint.resolution_amount = None
            complaint.admin_note = (payload.admin_note or '').strip() or None
            complaint.processed_by = admin_user_id
            complaint.processed_at = datetime.utcnow()
            self._notify_resolution(complaint, order, 'Your complaint was closed without a refund.')
            self.db.commit()
            self.db.refresh(complaint)
            return self._to_out(complaint, include_evidence=True)

        if action == 'refund_full':
            if not is_paid:
                raise HTTPException(status_code=400, detail='Order has no completed payment to refund')
            self._apply_paid_refund(order, complaint.guest_id, paid, paid)
            complaint.status = 'resolved'
            complaint.resolution_type = 'refund_full'
            complaint.resolution_amount = float(paid)
            complaint.admin_note = (payload.admin_note or '').strip() or None
            complaint.processed_by = admin_user_id
            complaint.processed_at = datetime.utcnow()
            self._notify_resolution(
                complaint,
                order,
                f'Approved: full refund of ${float(paid):.2f} was credited to your wallet.',
            )
            self.db.commit()
            self.db.refresh(complaint)
            return self._to_out(complaint, include_evidence=True)

        if action == 'refund_partial':
            if not is_paid:
                raise HTTPException(status_code=400, detail='Order has no completed payment to refund')
            if payload.amount is None or payload.amount <= Decimal('0'):
                raise HTTPException(status_code=400, detail='Partial refund requires a positive amount')
            refund_amt = payload.amount.quantize(Decimal('0.01'))
            if refund_amt > paid:
                raise HTTPException(
                    status_code=400,
                    detail='Refund cannot exceed the customer paid amount',
                )
            self._apply_paid_refund(order, complaint.guest_id, paid, refund_amt)
            complaint.status = 'resolved'
            complaint.resolution_type = 'refund_partial'
            complaint.resolution_amount = float(refund_amt)
            complaint.admin_note = (payload.admin_note or '').strip() or None
            complaint.processed_by = admin_user_id
            complaint.processed_at = datetime.utcnow()
            self._notify_resolution(
                complaint,
                order,
                f'Approved: ${float(refund_amt):.2f} was credited to your wallet.',
            )
            self.db.commit()
            self.db.refresh(complaint)
            return self._to_out(complaint, include_evidence=True)

        if action == 'waive_partial':
            if is_paid:
                raise HTTPException(
                    status_code=400,
                    detail='This order is already paid; use refund actions instead',
                )
            if payload.amount is None or payload.amount <= Decimal('0'):
                raise HTTPException(status_code=400, detail='Waiver requires a positive amount')
            waive_amt = payload.amount.quantize(Decimal('0.01'))
            current_due = resolve_guest_order_pay_amount(self.db, order, complaint.guest_id)
            if current_due <= Decimal('0'):
                raise HTTPException(status_code=400, detail='No pending amount to waive')
            if waive_amt > current_due:
                raise HTTPException(
                    status_code=400,
                    detail='Waiver cannot exceed the current amount due',
                )
            complaint.status = 'resolved'
            complaint.resolution_type = 'waive_partial'
            complaint.resolution_amount = float(waive_amt)
            complaint.admin_note = (payload.admin_note or '').strip() or None
            complaint.processed_by = admin_user_id
            complaint.processed_at = datetime.utcnow()
            self.db.flush()
            self._sync_pending_payment_amount(order, complaint.guest_id)
            self._notify_resolution(
                complaint,
                order,
                f'Approved: ${float(waive_amt):.2f} was waived from your pending payment.',
            )
            self.db.commit()
            self.db.refresh(complaint)
            return self._to_out(complaint, include_evidence=True)

        raise HTTPException(
            status_code=400,
            detail='Invalid action; use reject, refund_full, refund_partial, or waive_partial',
        )

    def _apply_paid_refund(
        self,
        order: ServiceOrderModel,
        guest_id: int,
        paid_cap: Decimal,
        refund_amt: Decimal,
    ) -> None:
        """Credit guest wallet and debit cleaner by the same refund amount (<= cleaner income)."""

        if not order.assigned_staff_id:
            raise HTTPException(status_code=400, detail='Order has no assigned cleaner to adjust')
        cleaner_income = self._cleaner_income_total(order.order_id, order.assigned_staff_id)
        if cleaner_income < refund_amt:
            raise HTTPException(
                status_code=400,
                detail='Cleaner income for this order is less than the refund amount',
            )
        if refund_amt > paid_cap:
            raise HTTPException(status_code=400, detail='Refund exceeds amount paid by customer')

        guest_wallet = self.db.query(WalletModel).filter(WalletModel.user_id == guest_id).first()
        if not guest_wallet:
            guest_wallet = WalletModel(user_id=guest_id, balance=Decimal('0'), frozen_balance=Decimal('0'))
            self.db.add(guest_wallet)
            self.db.flush()
            self.db.refresh(guest_wallet)
        guest_wallet_id = guest_wallet.id
        if guest_wallet_id is None:
            self.db.refresh(guest_wallet)
            guest_wallet_id = guest_wallet.id
        if guest_wallet_id is None:
            raise HTTPException(status_code=500, detail='Guest wallet id missing')

        guest_wallet.balance = Decimal(str(guest_wallet.balance or 0)) + refund_amt
        self.db.add(
            TransactionModel(
                wallet_id=guest_wallet_id,
                order_id=order.order_id,
                user_id=guest_id,
                type='refund',
                amount=refund_amt,
                status='completed',
                description=f'Complaint refund for order #{order.order_no}',
            )
        )

        cleaner_wallet = self.db.query(WalletModel).filter(
            WalletModel.user_id == order.assigned_staff_id
        ).first()
        if not cleaner_wallet:
            raise HTTPException(status_code=400, detail='Cleaner wallet not found')
        cleaner_balance = Decimal(str(cleaner_wallet.balance or 0))
        if cleaner_balance < refund_amt:
            raise HTTPException(
                status_code=400,
                detail='Cleaner wallet balance is insufficient for this deduction',
            )
        cleaner_wallet.balance = cleaner_balance - refund_amt
        cleaner_wallet_id = cleaner_wallet.id
        if cleaner_wallet_id is None:
            self.db.refresh(cleaner_wallet)
            cleaner_wallet_id = cleaner_wallet.id
        if cleaner_wallet_id is None:
            raise HTTPException(status_code=500, detail='Cleaner wallet id missing')

        self.db.add(
            TransactionModel(
                wallet_id=cleaner_wallet_id,
                order_id=order.order_id,
                user_id=order.assigned_staff_id,
                type='refund_clawback',
                amount=refund_amt,
                status='completed',
                description=f'Complaint refund clawback for order #{order.order_no}',
            )
        )

        if order.assigned_staff_id:
            notify_user(
                self.db,
                order.assigned_staff_id,
                'Complaint adjustment',
                f'${float(refund_amt):.2f} was deducted from your wallet for order {order.order_no}.',
                'warning',
                '/my-orders',
            )

    def _sync_pending_payment_amount(self, order: ServiceOrderModel, guest_id: int) -> None:
        """Set pending payment row to match payable after complaint waiver (flush complaint first)."""
        """Set pending payment row to match payable after complaint waiver (flush complaint first)."""
        pending = self._pending_payment_row(order.order_id, guest_id)
        new_due = resolve_guest_order_pay_amount(self.db, order, guest_id)
        if pending is not None:
            pending.amount = float(new_due)

    def _notify_resolution(self, complaint: ComplaintModel, order: ServiceOrderModel, body: str) -> None:
        """Send an in-app notification to the guest about the complaint resolution."""
        note = (complaint.admin_note or '').strip()
        content = body if not note else f'{body} Note: {note[:400]}'
        notify_user(
            self.db,
            complaint.guest_id,
            f'Complaint update: {order.order_no}',
            content[:4000],
            'info',
            '/my-orders',
        )

    def _to_out(self, row: ComplaintModel, include_evidence: bool) -> ComplaintOutSchema:
        """Convert a ComplaintModel into a ComplaintOutSchema with optional evidence."""
        evidence_list: List[ComplaintEvidenceSchema] = []
        if include_evidence:
            ev_rows = (
                self.db.query(ComplaintEvidenceModel)
                .filter(
                    ComplaintEvidenceModel.complaint_id == row.id,
                    ComplaintEvidenceModel.is_deleted == 0,
                )
                .order_by(ComplaintEvidenceModel.sort_order.asc())
                .all()
            )
            evidence_list = [
                ComplaintEvidenceSchema(id=e.id, photo_url=e.photo_url, sort_order=e.sort_order)
                for e in ev_rows
            ]

        order_no: Optional[str] = None
        guest_name: Optional[str] = None
        order = self._get_order(row.order_id)
        if order:
            order_no = order.order_no
        guest = self.db.query(UserModel).filter(UserModel.id == row.guest_id).first()
        if guest:
            guest_name = guest.full_name or guest.username

        return ComplaintOutSchema(
            id=row.id,
            order_id=row.order_id,
            guest_id=row.guest_id,
            title=row.title,
            description=row.description,
            status=row.status,
            resolution_type=row.resolution_type,
            resolution_amount=float(row.resolution_amount) if row.resolution_amount is not None else None,
            admin_note=row.admin_note,
            processed_by=row.processed_by,
            processed_at=row.processed_at,
            create_time=row.create_time,
            evidence=evidence_list,
            order_no=order_no,
            guest_name=guest_name,
        )
