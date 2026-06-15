from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Date, Time, Text
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class ConsumptionModel(Base):
    __tablename__ = 'consumption'

    consumption_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    remarks: Mapped[str] = mapped_column(String(200), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ScheduleModel(Base):
    __tablename__ = 'schedule'

    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    staff_id: Mapped[int] = mapped_column(Integer, nullable=False)
    work_date: Mapped[Date] = mapped_column(Date, nullable=False)
    shift: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    remarks: Mapped[str] = mapped_column(String(200), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReviewModel(Base):
    __tablename__ = 'review'

    review_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    guest_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    images: Mapped[str] = mapped_column(Text, nullable=True)
    reply: Mapped[str] = mapped_column(String(500), nullable=True)
    reply_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AnnouncementModel(Base):
    __tablename__ = 'announcement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str] = mapped_column(String(20), nullable=True)
    is_published: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    publish_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
