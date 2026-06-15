from datetime import datetime

from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class CustomerRequirementModel(Base):
    __tablename__ = 'customer_requirement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    guest_name: Mapped[str] = mapped_column(String(100), nullable=False)
    guest_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    guest_email: Mapped[str] = mapped_column(String(100), nullable=True)
    guest_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    property_type: Mapped[str] = mapped_column(String(50), nullable=False)
    bedroom: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    bathroom: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    living_room: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    kitchen: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    lawn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    car_space: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    square_footage: Mapped[float] = mapped_column(Float, nullable=True)

    service_type_id: Mapped[int] = mapped_column(Integer, nullable=True)
    service_type_name: Mapped[str] = mapped_column(String(100), nullable=True)
    preferred_time: Mapped[str] = mapped_column(String(200), nullable=True)
    budget: Mapped[float] = mapped_column(Float, nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    assigned_cleaner_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_published: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    publish_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
