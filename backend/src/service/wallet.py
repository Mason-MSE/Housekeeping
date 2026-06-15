# Standard library imports
from decimal import Decimal

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from model.notification import NotificationModel
from model.service_order import ServiceOrderModel
from model.service_type import ServiceTypeModel
from model.user import UserModel
from model.wallet import WalletModel, TransactionModel


class WalletService:
    def __init__(self, db: Session):
        self.db = db

    def get_wallet(self, user_id: int):
        wallet = self.db.query(WalletModel).filter(WalletModel.user_id == user_id).first()

        if not wallet:
            wallet = WalletModel(user_id=user_id, balance=1000.00, frozen_balance=0)
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)

        return wallet

    def recharge(self, user_id: int, amount: float):
        if amount <= 0:
            return {"error": "Recharge amount must be greater than 0", "status_code": 400}

        amount_decimal = Decimal(str(amount))

        wallet = self.db.query(WalletModel).filter(WalletModel.user_id == user_id).first()
        if wallet:
            wallet.balance = Decimal(str(wallet.balance)) + amount_decimal
        else:
            wallet = WalletModel(user_id=user_id, balance=amount_decimal, frozen_balance=0)
            self.db.add(wallet)
            self.db.flush()
            self.db.refresh(wallet)

        if wallet.id is None:
            self.db.refresh(wallet)

        transaction = TransactionModel(
            wallet_id=wallet.id,
            user_id=user_id,
            type='recharge',
            amount=amount_decimal,
            status='completed',
            description='User recharge'
        )
        self.db.add(transaction)
        self.db.commit()

        return {'message': 'Recharge successful', 'amount': amount}

    def get_transactions(self, user_id: int):
        transactions = self.db.query(TransactionModel).filter(
            TransactionModel.user_id == user_id
        ).order_by(TransactionModel.create_time.desc()).limit(20).all()
        return transactions

    def pay_order(self, user_id: int, order_id: int):

        order = self.db.query(ServiceOrderModel).filter(ServiceOrderModel.order_id == order_id).first()

        if not order:
            return {"error": "Order not found", "status_code": 404}

        if order.guest_id != user_id:
            return {"error": "You can only pay for your own orders", "status_code": 403}

        if order.status != 4:
            return {"error": "Order not completed, cannot pay", "status_code": 400}

        existing_payment = self.db.query(TransactionModel).filter(
            TransactionModel.order_id == order_id,
            TransactionModel.type == 'payment',
            TransactionModel.status == 'completed'
        ).first()

        if existing_payment:
            return {"error": "Order already paid", "status_code": 400}

        service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()

        if not service_type:
            return {"error": "Service type not found", "status_code": 400}

        price = Decimal(str(service_type.price))

        wallet = self.db.query(WalletModel).filter(WalletModel.user_id == user_id).first()

        if not wallet or wallet.balance < price:
            return {"error": "Insufficient balance", "status_code": 400}

        wallet.balance -= price

        transaction = TransactionModel(
            wallet_id=wallet.id,
            order_id=order_id,
            user_id=user_id,
            type='payment',
            amount=price,
            status='completed',
            description='Order payment'
        )
        self.db.add(transaction)

        if order.assigned_staff_id:
            cleaner_rate = 0.8
            cleaner_amount = Decimal(str(float(price) * cleaner_rate))

            cleaner_wallet = self.db.query(WalletModel).filter(WalletModel.user_id == order.assigned_staff_id).first()
            if cleaner_wallet:
                cleaner_wallet.balance += cleaner_amount
            else:
                cleaner_wallet = WalletModel(
                    user_id=order.assigned_staff_id,
                    balance=cleaner_amount
                )
                self.db.add(cleaner_wallet)
                self.db.flush()
                self.db.refresh(cleaner_wallet)

            if cleaner_wallet.id is None:
                self.db.refresh(cleaner_wallet)

            cleaner_wid = cleaner_wallet.id
            if cleaner_wid is None:
                return {"error": "Cleaner wallet id missing", "status_code": 500}

            cleaner_transaction = TransactionModel(
                wallet_id=cleaner_wid,
                order_id=order_id,
                user_id=order.assigned_staff_id,
                type='earning',
                amount=cleaner_amount,
                status='completed',
                description=f'Earning from order #{order_id}'
            )
            self.db.add(cleaner_transaction)

        self.db.commit()

        cleaner = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()

        customer_notif = NotificationModel(
            user_id=user_id,
            title=f'Payment Received for Order #{order.order_no}',
            content=f'Your payment of ${float(price)} for order #{order.order_no} has been processed successfully.',
            type='payment',
            is_read=0
        )
        self.db.add(customer_notif)

        if cleaner:
            cleaner_notif = NotificationModel(
                user_id=order.assigned_staff_id,
                title=f'Payment Received for Order #{order.order_no}',
                content=f'Payment of ${float(price)} has been received for order #{order.order_no}. Your earning will be processed after completion.',
                type='payment',
                is_read=0
            )
            self.db.add(cleaner_notif)

        self.db.commit()

        return {'message': 'Payment successful'}

    def settle_to_cleaner(self, admin_user_id: int, order_id: int):

        admin = self.db.query(UserModel).filter(UserModel.id == admin_user_id).first()
        if not admin or admin.role != 'admin':
            return {"error": "Only admin can settle payments to cleaners", "status_code": 403}

        order = self.db.query(ServiceOrderModel).filter(ServiceOrderModel.order_id == order_id).first()

        if not order:
            return {"error": "Order not found", "status_code": 404}

        if order.status != 4:
            return {"error": "Order not completed, cannot settle", "status_code": 400}

        if not order.assigned_staff_id:
            return {"error": "No cleaner assigned to this order", "status_code": 400}

        service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.id == order.service_type_id).first()

        if not service_type:
            return {"error": "Service type not found", "status_code": 400}

        price = float(service_type.price)
        cleaner_rate = 0.8
        cleaner_amount = price * cleaner_rate

        cleaner_wallet = self.db.query(WalletModel).filter(WalletModel.user_id == order.assigned_staff_id).first()
        if cleaner_wallet:
            cleaner_wallet.balance += cleaner_amount
        else:
            cleaner_wallet = WalletModel(user_id=order.assigned_staff_id, balance=cleaner_amount, frozen_balance=0)
            self.db.add(cleaner_wallet)
            self.db.flush()
            self.db.refresh(cleaner_wallet)

        if cleaner_wallet.id is None:
            self.db.refresh(cleaner_wallet)

        settle_wid = cleaner_wallet.id
        if settle_wid is None:
            return {"error": "Cleaner wallet id missing", "status_code": 500}

        transaction = TransactionModel(
            wallet_id=settle_wid,
            order_id=order_id,
            user_id=order.assigned_staff_id,
            type='settlement',
            amount=cleaner_amount,
            status='completed',
            description=f'Settlement for order {order.order_no}'
        )
        self.db.add(transaction)
        self.db.commit()

        return {'message': 'Settlement successful', 'amount': cleaner_amount, 'cleaner_id': order.assigned_staff_id}

    def get_cleaner_earnings(self, admin_user_id: int):

        admin = self.db.query(UserModel).filter(UserModel.id == admin_user_id).first()
        if not admin or admin.role != 'admin':
            return {"error": "Only admin can view cleaner earnings", "status_code": 403}

        results = self.db.query(
            UserModel.id,
            UserModel.full_name,
            UserModel.username
        ).filter(UserModel.role == 'cleaner').all()

        earnings = []
        for user_id, full_name, username in results:
            total = self.db.query(TransactionModel).filter(
                TransactionModel.user_id == user_id,
                TransactionModel.type == 'settlement',
                TransactionModel.status == 'completed'
            ).all()
            total_amount = sum(t.amount for t in total)

            completed_orders = self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.assigned_staff_id == user_id,
                ServiceOrderModel.status == 4
            ).count()

            earnings.append({
                'cleaner_id': user_id,
                'cleaner_name': full_name,
                'username': username,
                'completed_orders': completed_orders,
                'total_earnings': total_amount
            })

        return earnings
