from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Numeric, event,Date,Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column

from model.Base import Base




class BookingModel(Base):
    __tablename__ = 'booking'

    booking_id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, nullable=True)
    car_id = mapped_column(Integer, nullable=True)
    start_date = mapped_column(DateTime, nullable=True)
    end_date = mapped_column(DateTime, nullable=True)
    pickup_location = mapped_column(Integer, nullable=True)
    drop_location = mapped_column(Integer, nullable=True)
    status = mapped_column(Integer, nullable=True)
    notes = mapped_column(String, nullable=True)
    create_time = mapped_column(DateTime, nullable=True)
    modify_time = mapped_column(DateTime, nullable=True)
    is_deleted = mapped_column(Integer, nullable=True)
    pickup_time = mapped_column(DateTime, nullable=True)
    drop_time = mapped_column(DateTime, nullable=True)
