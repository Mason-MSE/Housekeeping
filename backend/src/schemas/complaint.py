"""Pydantic schemas for service-order complaints."""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ComplaintEvidenceSchema(BaseModel):
    """Single evidence image reference."""

    id: Optional[int] = None
    photo_url: str
    sort_order: int = 0

    class Config:
        from_attributes = True


class ComplaintCreateSchema(BaseModel):
    """Guest creates a complaint."""

    order_id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=8000)
    evidence_urls: List[str] = Field(default_factory=list, max_length=20)


class ComplaintResolveSchema(BaseModel):
    """Admin resolves a pending complaint."""

    action: str = Field(
        ...,
        description="reject | refund_full | refund_partial | waive_partial",
    )
    amount: Optional[Decimal] = Field(
        None,
        description="Required for refund_partial and waive_partial (positive number).",
    )
    admin_note: Optional[str] = Field(None, max_length=1000)


class ComplaintOutSchema(BaseModel):
    """Complaint returned to clients."""

    id: int
    order_id: int
    guest_id: int
    title: str
    description: Optional[str] = None
    status: str
    resolution_type: Optional[str] = None
    resolution_amount: Optional[float] = None
    admin_note: Optional[str] = None
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None
    create_time: Optional[datetime] = None
    evidence: List[ComplaintEvidenceSchema] = Field(default_factory=list)
    order_no: Optional[str] = None
    guest_name: Optional[str] = None

    class Config:
        from_attributes = True


class ComplaintListOutSchema(BaseModel):
    """Paginated complaint list."""

    items: List[ComplaintOutSchema]
    total: int


class ComplaintAdminDetailOutSchema(ComplaintOutSchema):
    """Admin complaint detail: guest-facing order snapshot (requirement, payment, staff)."""

    booking_detail: Optional[Dict[str, Any]] = Field(
        default=None,
        description='Same shape as portal customer order detail for the linked order/guest.',
    )
