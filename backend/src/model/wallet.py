from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class WalletModel(Base):
    """User wallet (balance/frozen balance) mapped to the 'wallet' table."""
    __tablename__ = 'wallet'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    frozen_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionModel(Base):
    """Wallet transaction ledger entry mapped to the 'transaction' table."""
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Explicit DB column name so INSERT always includes wallet_id (required by MySQL).
    wallet_id: Mapped[int] = mapped_column('wallet_id', Integer, nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='Order ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
