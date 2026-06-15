"""Resolve payable amount for guest orders (budget-first, then pending, price, default)."""
from decimal import Decimal
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from model.complaint import ComplaintModel
from model.customer_requirement import CustomerRequirementModel
from model.service_order import ServiceOrderModel
from model.service_type import ServiceTypeModel
from model.wallet import TransactionModel


def complaint_waiver_total_for_order(db: Session, order_id: int) -> Decimal:
    """Sum amounts from resolved waive_partial complaints (unpaid order adjustments).

    If complaint tables are not migrated yet, returns 0 so the rest of the app keeps working.
    """
    try:
        rows = (
            db.query(ComplaintModel)
            .filter(
                ComplaintModel.order_id == order_id,
                ComplaintModel.is_deleted == 0,
                ComplaintModel.status == 'resolved',
                ComplaintModel.resolution_type == 'waive_partial',
            )
            .all()
        )
    except SQLAlchemyError:
        return Decimal('0')
    total = Decimal('0')
    for row in rows:
        if row.resolution_amount is not None:
            total += Decimal(str(row.resolution_amount))
    return total


def resolve_guest_order_pay_amount(db: Session, order: ServiceOrderModel, guest_id: int) -> Decimal:
    """Amount to charge or show: linked requirement budget (>0), else pending payment, else service price, else 100.

    Args:
        db: Database session.
        order: Service order row.
        guest_id: Paying guest user id (must match pending payment filter).

    Returns:
        Decimal amount charged in the same currency unit as stored budget/price.
    """
    base: Optional[Decimal] = None
    if order.requirement_id:
        req = db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == order.requirement_id,
            CustomerRequirementModel.is_deleted == 0,
        ).first()
        if req is not None and req.budget is not None:
            budget_val = float(req.budget)
            if budget_val > 0:
                base = Decimal(str(round(budget_val, 2)))

    if base is None:
        pending = db.query(TransactionModel).filter(
            TransactionModel.order_id == order.order_id,
            TransactionModel.user_id == guest_id,
            TransactionModel.type == 'payment',
            TransactionModel.status == 'pending',
            TransactionModel.is_deleted == 0,
        ).first()
        if pending is not None and pending.amount is not None:
            base = Decimal(str(pending.amount))

    if base is None:
        service_type = db.query(ServiceTypeModel).filter(
            ServiceTypeModel.id == order.service_type_id,
            ServiceTypeModel.is_deleted == 0,
        ).first()
        if service_type is not None and service_type.price is not None:
            base = Decimal(str(service_type.price))

    if base is None:
        base = Decimal('100')

    waiver = complaint_waiver_total_for_order(db, order.order_id)
    due = base - waiver
    if due < Decimal('0'):
        return Decimal('0')
    return due.quantize(Decimal('0.01'))


def resolve_amount_for_new_pending_payment(db: Session, order: ServiceOrderModel) -> float:
    """Amount when creating the first pending payment at order completion (no pending row yet)."""
    if order.requirement_id:
        req = db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == order.requirement_id,
            CustomerRequirementModel.is_deleted == 0,
        ).first()
        if req is not None and req.budget is not None:
            budget_val = float(req.budget)
            if budget_val > 0:
                return round(budget_val, 2)

    service_type = db.query(ServiceTypeModel).filter(
        ServiceTypeModel.id == order.service_type_id,
    ).first()
    if service_type is not None and service_type.price is not None:
        return float(service_type.price)
    return 100.0
