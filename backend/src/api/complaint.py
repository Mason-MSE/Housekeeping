# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter, Depends, Query

# Local application imports
from core.dependencies import get_service, require_role
from model.user import UserModel
from schemas.complaint import (
    ComplaintAdminDetailOutSchema,
    ComplaintCreateSchema,
    ComplaintListOutSchema,
    ComplaintOutSchema,
    ComplaintResolveSchema,
)
from service.complaint_service import ComplaintService

router = APIRouter(prefix='/api/complaint', tags=['complaint'])


@router.post('', response_model=ComplaintOutSchema)
def create_complaint(
    payload: ComplaintCreateSchema,
    current_user: UserModel = Depends(require_role('guest', 'customer', 'user')),
    service: ComplaintService = Depends(get_service(ComplaintService)),
):
    """Guest files a complaint for a completed service order (within 15 days)."""
    return service.create_complaint(current_user.id, payload)


@router.get('/my', response_model=list[ComplaintOutSchema])
def list_my_complaints(
    current_user: UserModel = Depends(require_role('guest', 'customer', 'user')),
    service: ComplaintService = Depends(get_service(ComplaintService)),
):
    """List complaints submitted by the current guest."""
    return service.list_my_complaints(current_user.id)


@router.get('/admin', response_model=ComplaintListOutSchema)
def list_complaints_admin(
    status: Optional[str] = Query(None, description='Filter by complaint status'),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _auth: UserModel = Depends(require_role('administrator', 'admin', 'manager')),
    service: ComplaintService = Depends(get_service(ComplaintService)),
):
    """Admin: paginated complaint queue."""
    items, total = service.list_admin(status, page, page_size)
    return ComplaintListOutSchema(items=items, total=total)


@router.get('/admin/{complaint_id}', response_model=ComplaintAdminDetailOutSchema)
def get_complaint_admin(
    complaint_id: int,
    _auth: UserModel = Depends(require_role('administrator', 'admin', 'manager')),
    service: ComplaintService = Depends(get_service(ComplaintService)),
):
    """Admin: complaint detail with evidence."""
    return service.get_one(complaint_id)


@router.post('/admin/{complaint_id}/resolve', response_model=ComplaintOutSchema)
def resolve_complaint_admin(
    complaint_id: int,
    payload: ComplaintResolveSchema,
    current_user: UserModel = Depends(require_role('administrator', 'admin', 'manager')),
    service: ComplaintService = Depends(get_service(ComplaintService)),
):
    """Admin: reject, refund (paid), or waive pending amount (unpaid)."""
    return service.resolve_complaint(complaint_id, current_user.id, payload)
