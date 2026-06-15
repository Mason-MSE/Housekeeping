from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class ServiceDetailModel(Base):
    __tablename__ = 'service_detail'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    price_from: Mapped[float] = mapped_column(Float, nullable=True)
    price_to: Mapped[float] = mapped_column(Float, nullable=True)

    cover_image: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ServiceStepModel(Base):
    __tablename__ = 'service_step'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(200), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)

    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
