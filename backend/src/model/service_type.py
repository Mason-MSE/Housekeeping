from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base



class ServiceTypeModel(Base):
    """Service category/type definition mapped to the 'service_type' table."""
    __tablename__ = 'service_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    market_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
