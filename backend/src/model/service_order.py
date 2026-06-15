from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class ServiceOrderModel(Base):
    __tablename__ = 'service_order'

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_no: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    guest_id: Mapped[int] = mapped_column(Integer, nullable=False)
    service_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    requirement_id: Mapped[int] = mapped_column(Integer, nullable=True)
    assigned_staff_id: Mapped[int] = mapped_column(Integer, nullable=True)
    #: On-site address for portal / home cleaning (hotel flow may leave null).
    service_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    request_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    scheduled_start: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    scheduled_end: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    actual_complete: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    remarks: Mapped[str] = mapped_column(String(500), nullable=True)
    guest_feedback: Mapped[str] = mapped_column(String(500), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)

    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class OrderPhotoModel(Base):
    __tablename__ = 'order_photo'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_type: Mapped[str] = mapped_column(String(20), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    uploaded_by: Mapped[int] = mapped_column(Integer, nullable=False)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
