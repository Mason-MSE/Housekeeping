from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class InspectionModel(Base):
    __tablename__ = 'inspection'

    inspection_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    inspector_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cleaner_id: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    issues: Mapped[str] = mapped_column(Text, nullable=True)
    photos: Mapped[str] = mapped_column(Text, nullable=True)
    inspection_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    reinspection_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
