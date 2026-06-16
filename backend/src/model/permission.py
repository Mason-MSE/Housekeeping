from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import mapped_column

from model.Base import Base


class PermissionModel(Base):
    """System permission entry mapped to the 'permission' table."""
    __tablename__ = 'permission'

    id = mapped_column(Integer, primary_key=True)
    permission_name = mapped_column(String(100), nullable=False)
    permission_code = mapped_column(String(100), nullable=False, unique=True)
    description = mapped_column(String(255), nullable=True)
    create_time = mapped_column(DateTime, nullable=True)
    modify_time = mapped_column(DateTime, nullable=True)
    is_deleted = mapped_column(Integer, nullable=True)
