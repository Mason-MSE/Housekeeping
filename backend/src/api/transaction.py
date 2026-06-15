from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from model.notification import NotificationModel
from model.user import UserModel
from model.service_order import ServiceOrderModel
from model.wallet import WalletModel, TransactionModel
from core.dependencies import require_permission
from schemas.housekeeping import PaymentSchema, TransactionSchema, OrderReviewSchema
from service.order_payment_amount import resolve_guest_order_pay_amount
from service.in_app_notify import notify_user


router = APIRouter(prefix='/api/transaction', tags=['transaction'])


@router.post('/pay', response_model=TransactionSchema)
def create_payment(
    payment_data: PaymentSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    try:
        order = db.query(ServiceOrderModel).filter(
            ServiceOrderModel.order_id == payment_data.order_id,
            ServiceOrderModel.is_deleted == 0
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail='Order not found')

        if order.guest_id != current_user.id:
            raise HTTPException(status_code=403, detail='You can only pay for your own orders')

        # Some parts of the portal flow mark a finished job as "Completed" (4),
        # while the payment flow uses "Pending Payment" (5). Allow payment from either.
        if order.status not in (4, 5):
            raise HTTPException(status_code=400, detail='Order is not payable in its current status')

        existing_paid = db.query(TransactionModel).filter(
            TransactionModel.order_id == payment_data.order_id,
            TransactionModel.user_id == current_user.id,
            TransactionModel.type == 'payment',
            TransactionModel.status == 'completed'
        ).first()
        if existing_paid:
            raise HTTPException(status_code=400, detail='Payment already exists for this order')

        existing_pending = db.query(TransactionModel).filter(
            TransactionModel.order_id == payment_data.order_id,
            TransactionModel.user_id == current_user.id,
            TransactionModel.type == 'payment',
            TransactionModel.status == 'pending'
        ).first()

        amount_decimal = resolve_guest_order_pay_amount(db, order, current_user.id)
        if existing_pending is not None:
            existing_pending.amount = amount_decimal

        customer_wallet = db.query(WalletModel).filter(WalletModel.user_id == current_user.id).first()
        if not customer_wallet:
            customer_wallet = WalletModel(user_id=current_user.id, balance=Decimal("0"), frozen_balance=Decimal("0"))
            db.add(customer_wallet)
            db.flush()
            db.refresh(customer_wallet)

        current_balance = Decimal(str(customer_wallet.balance or 0))
        if current_balance < amount_decimal:
            raise HTTPException(status_code=400, detail='Insufficient wallet balance')

        customer_wallet.balance = current_balance - amount_decimal

        if order.assigned_staff_id:
            cleaner_wallet = db.query(WalletModel).filter(WalletModel.user_id == order.assigned_staff_id).first()
            if not cleaner_wallet:
                cleaner_wallet = WalletModel(user_id=order.assigned_staff_id, balance=Decimal("0"), frozen_balance=Decimal("0"))
                db.add(cleaner_wallet)
                db.flush()
                db.refresh(cleaner_wallet)
            elif cleaner_wallet.id is None:
                db.refresh(cleaner_wallet)

            cleaner_wallet_id = cleaner_wallet.id
            if cleaner_wallet_id is None:
                raise HTTPException(status_code=500, detail='Cleaner wallet id missing after create')

            cleaner_wallet.balance = Decimal(str(cleaner_wallet.balance or 0)) + amount_decimal

            cleaner_transaction = TransactionModel(
                wallet_id=cleaner_wallet_id,
                order_id=order.order_id,
                user_id=order.assigned_staff_id,
                type='income',
                amount=amount_decimal,
                status='completed',
                description=f'Income for order #{order.order_no}'
            )
            db.add(cleaner_transaction)

        if existing_pending:
            existing_pending.status = 'completed'
            existing_pending.description = (
                f'Payment completed via {payment_data.payment_method} for order #{order.order_no}'
            )
            transaction = existing_pending
        else:
            customer_wallet_id = customer_wallet.id
            if customer_wallet_id is None:
                db.refresh(customer_wallet)
                customer_wallet_id = customer_wallet.id
            if customer_wallet_id is None:
                raise HTTPException(status_code=500, detail='Customer wallet id missing after create')
            transaction = TransactionModel(
                wallet_id=customer_wallet_id,
                order_id=order.order_id,
                user_id=current_user.id,
                type='payment',
                amount=amount_decimal,
                status='completed',
                description=f'Payment via {payment_data.payment_method} for order #{order.order_no}'
            )
            db.add(transaction)

        order.status = 6

        customer_notif = NotificationModel(
            user_id=current_user.id,
            title=f'Payment Completed: {order.order_no}',
            content=(
                f'You paid ${float(amount_decimal):.2f} for order {order.order_no}.\n\nOpen: /my-orders'
            ),
            type='payment',
            is_read=0,
        )
        db.add(customer_notif)

        if order.assigned_staff_id:
            cleaner_notif = NotificationModel(
                user_id=order.assigned_staff_id,
                title=f'Income Received: {order.order_no}',
                content=(
                    f'You received ${float(amount_decimal):.2f} for order {order.order_no}.\n\nOpen: /my-orders'
                ),
                type='payment',
                is_read=0,
            )
            db.add(cleaner_notif)

        db.commit()
        db.refresh(transaction)
        return transaction
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Payment processing failed: {str(exc)}') from exc


@router.get('/order/{order_id}', response_model=TransactionSchema)
def get_transaction_by_order(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    transaction = db.query(TransactionModel).filter(
        TransactionModel.order_id == order_id,
        TransactionModel.user_id == current_user.id,
        TransactionModel.type == 'payment'
    ).order_by(TransactionModel.create_time.desc()).first()
    if not transaction:
        raise HTTPException(status_code=404, detail='Transaction not found')
    return transaction


@router.post('/review', response_model=dict)
def submit_review(
    review_data: OrderReviewSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    order = db.query(ServiceOrderModel).filter(
        ServiceOrderModel.order_id == review_data.order_id,
        ServiceOrderModel.is_deleted == 0
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    
    if order.guest_id != current_user.id:
        raise HTTPException(status_code=403, detail='You can only review your own orders')
    
    if order.status != 6:
        raise HTTPException(status_code=400, detail='Order is not in pending review status')
    
    rating_val = review_data.rating
    if rating_val < 0.5 or rating_val > 5:
        raise HTTPException(status_code=400, detail='Rating must be between 0.5 and 5')
    if abs(rating_val * 2 - round(rating_val * 2)) > 1e-9:
        raise HTTPException(status_code=400, detail='Rating must be in half-star steps (0.5 increments)')

    # Match service_order.rate_order: store rating * 10 so half-stars work (e.g. 2 -> 20, 2.5 -> 25)
    order.rating = int(round(rating_val * 10))
    order.guest_feedback = review_data.comment
    order.status = 7

    if order.assigned_staff_id:
        comment_snip = (review_data.comment or '')[:200]
        body = f'Order {order.order_no}: {rating_val} stars.'
        if comment_snip:
            body = f'{body} — {comment_snip}'
        notify_user(
            db,
            order.assigned_staff_id,
            'New review from customer',
            body,
            'info',
            '/my-orders',
        )

    db.commit()

    return {'ok': True, 'message': 'Review submitted successfully'}
