from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import mapped_column

from model.Base import Base


class RoomModel(Base):
    __tablename__ = 'room'

    id = mapped_column(Integer, primary_key=True)
    room_number = mapped_column(String(20), nullable=False)
    floor = mapped_column(Integer, nullable=True)
    room_type = mapped_column(String(50), nullable=True)
    capacity = mapped_column(Integer, nullable=True)
    price = mapped_column(Float, nullable=True)
    status = mapped_column(Integer, nullable=True)
    create_time = mapped_column(DateTime, nullable=True)
    modify_time = mapped_column(DateTime, nullable=True)
    is_deleted = mapped_column(Integer, nullable=True)
