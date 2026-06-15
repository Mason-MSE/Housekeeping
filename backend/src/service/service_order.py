# Standard library imports
import random
import string
from datetime import datetime
from typing import List, Optional

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from cruds.CRUDBase import CRUDBase
from model.notification import NotificationModel
from model.service_order import ServiceOrderModel
from model.user import UserModel
from model.wallet import WalletModel, TransactionModel
from schemas.housekeeping import ServiceOrderCreateSchema, ServiceOrderUpdateSchema
from service.order_payment_amount import resolve_amount_for_new_pending_payment
from service.in_app_notify import notify_user


def generate_order_no():
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"SO{date_str}{random_str}"


class ServiceOrderCRUD(CRUDBase[ServiceOrderModel, ServiceOrderCreateSchema, ServiceOrderUpdateSchema]):
    pass


service_order_crud = ServiceOrderCRUD(ServiceOrderModel)


class ServiceOrderService:
    def __init__(self, db: Session):
        self.db = db

    def _enrich_with_staff_name(self, order: ServiceOrderModel) -> dict:
        order_dict = {
            'order_id': order.order_id,
            'order_no': order.order_no,
            'guest_id': order.guest_id,
            'service_type_id': order.service_type_id,
            'assigned_staff_id': order.assigned_staff_id,
            'assigned_staff_name': None,
            'status': order.status,
            'priority': order.priority,
            'request_time': order.request_time,
            'scheduled_start': order.scheduled_start,
            'scheduled_end': order.scheduled_end,
            'actual_start': order.actual_start,
            'actual_complete': order.actual_complete,
            'remarks': order.remarks,
            'rating': order.rating,
            'create_time': order.create_time,
        }
        if order.assigned_staff_id:
            staff = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
            if staff:
                order_dict['assigned_staff_name'] = staff.full_name
        return order_dict

    def get_all(self):
        orders = service_order_crud.get_all(self.db)
        return [self._enrich_with_staff_name(o) for o in orders]

    def get(self, id: int):
        order = service_order_crud.get(self.db, id)
        if order:
            return self._enrich_with_staff_name(order)
        return None

    def get(self, id: int):
        return service_order_crud.get(self.db, id)

    def get_by_cleaner(self, cleaner_id: int):
        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0
        ).all()
        return [self._enrich_with_staff_name(o) for o in orders]

    def get_by_guest(self, guest_id: int):
        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.guest_id == guest_id,
            ServiceOrderModel.is_deleted == 0
        ).all()
        return [self._enrich_with_staff_name(o) for o in orders]

    def create(self, obj_in: ServiceOrderCreateSchema, guest_id: int):
        data = obj_in.dict()
        data['order_no'] = generate_order_no()
        data['guest_id'] = guest_id
        data['status'] = 0
        obj = ServiceOrderModel(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._enrich_with_staff_name(obj)

    def update(self, id: int, obj_in: ServiceOrderUpdateSchema):
        db_obj = service_order_crud.get(self.db, id)
        if not db_obj:
            return None
        updated = service_order_crud.update(self.db, db_obj, obj_in)
        if updated:
            return self._enrich_with_staff_name(updated)
        return None

    def delete(self, id: int):
        db_obj = service_order_crud.get(self.db, id)
        if not db_obj:
            return False
        return service_order_crud.soft_delete(self.db, db_obj)

    def get_paginated(self, page: int = 1, page_size: int = 10, filters: dict = None, order_by: str = None):
        skip = (page - 1) * page_size
        total, items = service_order_crud.get_paginated(self.db, skip, page_size, filters, order_by)
        enriched_items = [self._enrich_with_staff_name(item) for item in items]
        return total, enriched_items

    def assign_staff(self, order_id: int, staff_id: int):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.assigned_staff_id = staff_id
        order.status = 1
        self.db.commit()
        self.db.refresh(order)

        notification = NotificationModel(
            user_id=staff_id,
            title='New Task Assigned',
            content=f'You have been assigned order {order.order_no}\n\nOpen: /my-orders',
            type='info',
        )
        self.db.add(notification)
        self.db.commit()

        return self._enrich_with_staff_name(order)

    def start_work(self, order_id: int):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.status = 2
        order.actual_start = datetime.utcnow()
        notify_user(
            self.db,
            order.guest_id,
            'Cleaning started',
            f'Your order {order.order_no} is now in progress.',
            'info',
            '/my-orders',
        )
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)

    def complete(self, order_id: int):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.status = 5
        order.actual_complete = datetime.utcnow()

        # Create pending payment record in transaction table if not exists.
        existing_payment = self.db.query(TransactionModel).filter(
            TransactionModel.order_id == order.order_id,
            TransactionModel.user_id == order.guest_id,
            TransactionModel.type == 'payment'
        ).first()
        if not existing_payment:
            amount = resolve_amount_for_new_pending_payment(self.db, order)
            customer_wallet = self.db.query(WalletModel).filter(WalletModel.user_id == order.guest_id).first()
            if not customer_wallet:
                customer_wallet = WalletModel(user_id=order.guest_id, balance=1000.0, frozen_balance=0.0)
                self.db.add(customer_wallet)
                self.db.flush()
                self.db.refresh(customer_wallet)
            elif customer_wallet.id is None:
                self.db.refresh(customer_wallet)

            guest_wallet_id = customer_wallet.id
            if guest_wallet_id is None:
                raise ValueError('Guest wallet id missing after create')

            self.db.add(TransactionModel(
                wallet_id=guest_wallet_id,
                order_id=order.order_id,
                user_id=order.guest_id,
                type='payment',
                amount=amount,
                status='pending',
                description=f'Pending payment for order #{order.order_no}'
            ))

        notification = NotificationModel(
            user_id=order.guest_id,
            title='Order Completed - Payment Required',
            content=(
                f'Your order {order.order_no} has been completed. Please complete payment.\n\nOpen: /my-orders'
            ),
            type='success',
        )
        if order.assigned_staff_id:
            notify_user(
                self.db,
                order.assigned_staff_id,
                'Order marked complete',
                f'Order {order.order_no} is awaiting customer payment.',
                'info',
                '/my-orders',
            )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(order)

        return self._enrich_with_staff_name(order)

    def cancel_order(self, order_id: int, reason: str = None):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.status = 5
        if reason:
            order.remarks = (order.remarks or '') + f' [Cancelled: {reason}]'
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)

    def rate_order(self, order_id: int, rating: float, comment: str = None):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        if rating < 0.5 or rating > 5:
            raise ValueError("Rating must be between 0.5 and 5")
        if (rating * 2) % 1 != 0:
            raise ValueError("Rating must be in 0.5 increments")
        order.rating = int(round(rating * 10))
        if comment:
            order.guest_feedback = comment
        if order.assigned_staff_id:
            comment_snip = (comment or '')[:200]
            body = f'Order {order.order_no}: {rating} stars.'
            if comment_snip:
                body = f'{body} — {comment_snip}'
            notify_user(
                self.db,
                order.assigned_staff_id,
                'New review from customer',
                body,
                'info',
                '/my-orders',
            )
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)

    def upload_photo(self, order_id: int, photo_type: str, photo_data: str):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        if photo_type == 'before':
            order.before_photo = photo_data
        elif photo_type == 'after':
            order.after_photo = photo_data
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)
