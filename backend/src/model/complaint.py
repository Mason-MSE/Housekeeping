"""SQLAlchemy models for customer complaints on service orders."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base


class ComplaintModel(Base):
    """A guest-submitted complaint linked to one service order."""

    __tablename__ = 'complaint'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    guest_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    resolution_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    resolution_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    admin_note: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    processed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ComplaintEvidenceModel(Base):
    """Evidence image (e.g. base64 data URL) attached to a complaint."""

    __tablename__ = 'complaint_evidence'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(Integer, ForeignKey('complaint.id'), nullable=False)
    # Base64 data URLs exceed MySQL TEXT (~64KB); use MEDIUMTEXT on MySQL.
    photo_url: Mapped[str] = mapped_column(
        Text().with_variant(MEDIUMTEXT(), 'mysql'),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
