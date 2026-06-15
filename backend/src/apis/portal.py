from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from core.dependencies import get_current_user_optional, get_service
from model.user import UserModel
from service.portal_service import PortalService
from schemas.portal import (
    PortalServiceTypeSchema,
    PortalRoomSchema,
    PortalOrderCreateSchema,
    PortalOrderSchema,
    ServiceTypeDetailSchema,
    CompanyInfoSchema,
    ReviewSchema,
    CustomerRequirementSchema,
    CleanerApplicationCreateSchema,
    CleanerApplicationSchema,
    CleanerTaskSchema,
    AdminRequirementSchema,
    AdminCleanerSchema,
    CleanerSchema,
    CleanerDetailSchema
)

router = APIRouter(prefix='/api/portal', tags=['portal'])


@router.get('/services', response_model=list[PortalServiceTypeSchema])
def get_portal_services(service: PortalService = Depends(get_service(PortalService))):
    """Get all active service types for portal display"""
    return service.get_all_service_types()


@router.get('/services/{type_id}', response_model=ServiceTypeDetailSchema)
def get_service_detail(type_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get service type detail"""
    return service.get_service_type_detail(type_id)


@router.get('/rooms', response_model=list[PortalRoomSchema])
def get_portal_rooms(service: PortalService = Depends(get_service(PortalService))):
    """Get all active rooms for portal"""
    return service.get_all_rooms()


@router.post('/order', response_model=dict)
def create_portal_order(
    order_data: PortalOrderCreateSchema,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    service: PortalService = Depends(get_service(PortalService)),
):
    """Create a new order from portal"""
    return service.create_order(order_data.model_dump(), current_user=current_user)


@router.get('/orders/{phone}', response_model=list[PortalOrderSchema])
def get_portal_orders(phone: str, service: PortalService = Depends(get_service(PortalService))):
    """Get orders by phone number"""
    return service.get_orders_by_phone(phone)


@router.get('/stats', response_model=dict)
def get_portal_stats(service: PortalService = Depends(get_service(PortalService))):
    """Get portal statistics"""
    return service.get_stats()


@router.get('/company-info', response_model=CompanyInfoSchema)
def get_company_info(service: PortalService = Depends(get_service(PortalService))):
    """Get company info for portal"""
    return service.get_company_info()


@router.get('/reviews', response_model=list[ReviewSchema])
def get_portal_reviews(limit: int = 10, offset: int = 0, service: PortalService = Depends(get_service(PortalService))):
    """Get customer reviews for portal"""
    return service.get_reviews(limit, offset)


@router.get('/reviews/count', response_model=dict)
def get_reviews_count(service: PortalService = Depends(get_service(PortalService))):
    """Get total reviews count"""
    return service.get_reviews_count()


@router.get('/reviews/{review_id}', response_model=ReviewSchema)
def get_review_detail(review_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get single review detail"""
    return service.get_review_detail(review_id)


@router.get('/cleaners', response_model=list[CleanerSchema])
def get_portal_cleaners(
    sort_by: str = None,
    search: str = None,
    service: PortalService = Depends(get_service(PortalService))
):
    """Get all active cleaners for portal with optional sorting and filtering"""
    return service.get_all_cleaners(sort_by=sort_by, search=search)


@router.get('/cleaners/{cleaner_id}', response_model=CleanerDetailSchema)
def get_cleaner_detail(cleaner_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get cleaner detail"""
    return service.get_cleaner_detail(cleaner_id)


@router.get('/cleaner-tasks/{cleaner_id}', response_model=list[CleanerTaskSchema])
def get_cleaner_tasks(cleaner_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get all tasks for a cleaner"""
    return service.get_cleaner_tasks(cleaner_id)


@router.get('/my-applications/{cleaner_id}', response_model=list[CleanerApplicationSchema])
def get_cleaner_applications(cleaner_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get all applications by a cleaner"""
    return service.get_cleaner_applications(cleaner_id)


@router.get('/requirements', response_model=list[CustomerRequirementSchema])
def get_portal_requirements(limit: int = 50, service: PortalService = Depends(get_service(PortalService))):
    """Get all requirements for portal"""
    return service.get_all_requirements(limit)


@router.get('/requirements/{phone}', response_model=list[CustomerRequirementSchema])
def get_requirements_by_phone(phone: str, service: PortalService = Depends(get_service(PortalService))):
    """Get customer requirements by phone"""
    return service.get_requirements_by_phone(phone)


@router.post('/requirement', response_model=dict)
def create_requirement(requirement_data: dict, service: PortalService = Depends(get_service(PortalService))):
    """Create a new customer requirement"""
    return service.create_requirement(requirement_data)


@router.post('/apply', response_model=dict)
def apply_for_requirement(application_data: CleanerApplicationCreateSchema, service: PortalService = Depends(get_service(PortalService))):
    """Apply for a customer requirement"""
    return service.apply_for_requirement(application_data)


@router.get('/applications/{requirement_id}', response_model=list[CleanerApplicationSchema])
def get_applications(requirement_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get applications for a requirement"""
    return service.get_applications(requirement_id)


@router.get('/admin/requirements', response_model=list[AdminRequirementSchema])
def get_admin_requirements(status: Optional[int] = None, limit: int = 1000, service: PortalService = Depends(get_service(PortalService))):
    """Get all requirements for admin management"""
    return service.get_admin_requirements(status, limit)


@router.get('/admin/cleaners', response_model=list[AdminCleanerSchema])
def get_admin_cleaners(service: PortalService = Depends(get_service(PortalService))):
    """Get all cleaners with their workload stats for admin"""
    return service.get_admin_cleaners()


@router.post('/admin/assign-requirement')
def assign_requirement_to_cleaner(requirement_id: int, cleaner_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Assign a requirement to a specific cleaner"""
    result = service.assign_requirement_to_cleaner(requirement_id, cleaner_id)
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('message', 'Assignment failed'))
    return result
