from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class CleanerApplicationModel(Base):
    __tablename__ = 'cleaner_application'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cleaner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cleaner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    offered_price: Mapped[float] = mapped_column(Float, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
