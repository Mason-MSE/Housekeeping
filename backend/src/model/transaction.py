from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base


class PaymentTransactionModel(Base):
    """Payment transaction record linked to a service order, mapped to the 'payment_transaction' table."""
    __tablename__ = 'payment_transaction'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_no: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('service_order.order_id'), nullable=False)
    requirement_id: Mapped[int] = mapped_column(Integer, ForeignKey('customer_requirement.id'), nullable=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    cleaner_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=True)
    
    amount: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)
    payment_status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payment_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
