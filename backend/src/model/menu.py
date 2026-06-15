from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base


class MenuModel(Base):
    __tablename__ = 'menu'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    menu_name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=True)
    component: Mapped[str] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int] = mapped_column(Integer, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    creator: Mapped[int] = mapped_column(Integer, nullable=True)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    modifier: Mapped[int] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
