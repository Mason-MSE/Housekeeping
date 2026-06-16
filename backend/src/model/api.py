from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base


class ApiModel(Base):
    """API endpoint registry mapped to the 'api' table."""
    __tablename__ = 'api'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_path: Mapped[str] = mapped_column(String(255), nullable=False)
    api_method: Mapped[str] = mapped_column(String(20), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permission.id', ondelete='CASCADE'), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    creator: Mapped[int] = mapped_column(Integer, nullable=True)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    modifier: Mapped[int] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
