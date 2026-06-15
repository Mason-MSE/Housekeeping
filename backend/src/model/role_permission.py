from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base


class RolePermissionModel(Base):
    __tablename__ = 'role_permission'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permission.id', ondelete='CASCADE'), nullable=False)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    creator: Mapped[int] = mapped_column(Integer, nullable=True)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    modifier: Mapped[int] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
