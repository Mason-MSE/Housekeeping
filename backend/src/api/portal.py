# Standard library imports
from typing import Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException

# Local application imports
from core.dependencies import get_current_user_optional, get_service, require_role
from model.user import UserModel
from schemas.portal import (
    AdminCleanerSchema,
    CleanerApplicationCreateSchema,
    CleanerApplicationSchema,
    CleanerDetailSchema,
    CleanerSchema,
    CleanerTaskSchema,
    CompanyInfoSchema,
    CustomerRequirementCustomerCreateSchema,
    CustomerRequirementSchema,
    PortalOrderCreateSchema,
    PortalOrderSchema,
    PortalRoomSchema,
    PortalServiceTypeSchema,
    ReviewSchema,
    ServiceTypeDetailSchema,
)
from service.portal_service import PortalService

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
    """Create a new order from portal (maps to ``service_order``)."""
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
    return service.get_cleaner_tasks(cleaner_id, None, 20, 0)


@router.get('/cleaner-tasks/{cleaner_id}/paginated')
def get_cleaner_tasks_paginated(
    cleaner_id: int,
    status: int = None,
    page: int = 1,
    page_size: int = 20,
    service: PortalService = Depends(get_service(PortalService))
):
    """Get paginated tasks for a cleaner"""
    offset = (page - 1) * page_size
    return service.get_cleaner_tasks(cleaner_id, status, page_size, offset)


@router.get('/my-applications/{cleaner_id}', response_model=list[CleanerApplicationSchema])
def get_cleaner_applications(cleaner_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Get all applications by a cleaner"""
    return service.get_cleaner_applications(cleaner_id)


@router.get('/my-applications/{cleaner_id}/paginated')
def get_cleaner_applications_paginated(
    cleaner_id: int,
    status: int = None,
    page: int = 1,
    page_size: int = 20,
    service: PortalService = Depends(get_service(PortalService))
):
    """Get paginated applications by a cleaner"""
    offset = (page - 1) * page_size
    return service.get_cleaner_applications_paginated(cleaner_id, status, page_size, offset)


@router.get('/cleaner/my-requirements/{cleaner_id}')
def get_cleaner_requirements(
    cleaner_id: int,
    status: int = None,
    page: int = 1,
    page_size: int = 20,
    current_user: UserModel = Depends(require_role('cleaner', 'staff', 'employee')),
    service: PortalService = Depends(get_service(PortalService))
):
    """Cleaner: requirements you applied for or that were assigned to you (not customer-posted list)."""
    if current_user.id != cleaner_id:
        raise HTTPException(status_code=403, detail='You can only view your own cleaner requirement list')
    offset = (page - 1) * page_size
    return service.get_cleaner_requirements(cleaner_id, status, page_size, offset)


@router.get('/requirements', response_model=list[CustomerRequirementSchema])
def get_portal_requirements( service: PortalService = Depends(get_service(PortalService))):
    """Get all requirements for portal"""
    return service.get_all_requirements()


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
def get_applications(requirement_id: int, phone: str = None, service: PortalService = Depends(get_service(PortalService))):
    """Get applications for a requirement. Phone must match the requirement's guest_phone"""
    requirement = service.get_requirement_by_id(requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail='Requirement not found')
    if phone and requirement.get('guest_phone') != phone:
        raise HTTPException(status_code=403, detail='You can only view applications for your own requirement')
    return service.get_applications(requirement_id)


@router.get('/admin/requirements')
def get_admin_requirements(
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    guest_name: str = None,
    guest_phone: str = None,
    property_type: str = None,
    service_type: str = None,
    start_date: str = None,
    end_date: str = None,
    service: PortalService = Depends(get_service(PortalService))
):
    """Get all requirements for admin management with pagination and filters"""
    offset = (page - 1) * page_size
    return service.get_admin_requirements(status, page_size, offset, guest_name, guest_phone, property_type, service_type, start_date, end_date)


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


@router.delete('/admin/requirement/{requirement_id}')
def delete_requirement(requirement_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Delete a requirement (hard delete)"""
    return service.delete_requirement(requirement_id)


@router.post('/admin/requirement/{requirement_id}/hide')
def hide_requirement(requirement_id: int, service: PortalService = Depends(get_service(PortalService))):
    """Hide a requirement (soft delete)"""
    return service.hide_requirement(requirement_id)


@router.get('/admin/tasks')
def get_all_cleaner_tasks(
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    order_no: str = None,
    cleaner_name: str = None,
    start_date: str = None,
    end_date: str = None,
    service: PortalService = Depends(get_service(PortalService))
):
    """Get all cleaner tasks for admin with pagination and filters"""
    offset = (page - 1) * page_size
    return service.get_all_cleaner_tasks(status, page_size, offset, order_no, cleaner_name, start_date, end_date)


@router.get('/customer/requirements/{user_id}')
def get_customer_requirements(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    requirement_id: int = None,
    status: int = None,
    property_type: str = None,
    service_type: str = None,
    is_published: int = None,
    current_user: UserModel = Depends(require_role('guest', 'customer', 'user')),
    service: PortalService = Depends(get_service(PortalService))
):
    """Customer: requirements you created and posted (optionally filter by portal draft vs live)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail='You can only access your own requirements')
    offset = (page - 1) * page_size
    return service.get_customer_requirements(
        user_id,
        page_size,
        offset,
        requirement_id,
        status,
        property_type,
        service_type,
        is_published,
    )


@router.post('/customer/requirement')
def create_customer_requirement(
    body: CustomerRequirementCustomerCreateSchema,
    current_user: UserModel = Depends(require_role('guest', 'customer', 'user')),
    service: PortalService = Depends(get_service(PortalService)),
):
    """Customer: create a requirement from the management module; optional portal listing."""
    return service.create_customer_requirement(current_user.id, body.model_dump())


@router.put('/customer/requirement/{requirement_id}')
def update_customer_requirement(
    requirement_id: int,
    body: CustomerRequirementCustomerCreateSchema,
    current_user: UserModel = Depends(require_role('guest', 'customer', 'user')),
    service: PortalService = Depends(get_service(PortalService)),
):
    """Customer: update own requirement while it is still unpublished (draft)."""
    result = service.update_customer_requirement(
        current_user.id, requirement_id, body.model_dump()
    )
    if not result.get('success'):
        raise HTTPException(
            status_code=400, detail=result.get('message', 'Update failed')
        )
    return result


@router.post('/customer/approve-cleaner')
def approve_cleaner_for_requirement(
    requirement_id: int,
    cleaner_id: int,
    service: PortalService = Depends(get_service(PortalService))
):
    """Customer approves/assigns a cleaner for their requirement"""
    return service.approve_cleaner_for_requirement(requirement_id, cleaner_id)


@router.get('/customer/bookings/{user_id}')
def get_customer_bookings(user_id: int, page: int = 1, page_size: int = 20, service: PortalService = Depends(get_service(PortalService))):
    """Get all bookings for a customer with pagination"""
    offset = (page - 1) * page_size
    return service.get_customer_bookings(user_id, page_size, offset)


@router.get('/customer/booking/{order_id}')
def get_customer_booking_detail(order_id: int, user_id: int = None, service: PortalService = Depends(get_service(PortalService))):
    """Get detailed booking information for a customer"""
    if not user_id:
        return {'success': False, 'message': 'user_id is required'}
    result = service.get_order_detail(order_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail='Order not found')
    return result


@router.get('/cleaner/bookings/{cleaner_id}')
def get_cleaner_bookings(cleaner_id: int, page: int = 1, page_size: int = 20, service: PortalService = Depends(get_service(PortalService))):
    """Get all bookings for a cleaner (orders assigned to this cleaner)"""
    offset = (page - 1) * page_size
    return service.get_cleaner_bookings(cleaner_id, page_size, offset)


@router.get('/cleaner/booking/{order_id}')
def get_cleaner_booking_detail(order_id: int, cleaner_id: int = None, service: PortalService = Depends(get_service(PortalService))):
    """Get detailed booking information for a cleaner"""
    if not cleaner_id:
        return {'success': False, 'message': 'cleaner_id is required'}
    result = service.get_cleaner_order_detail(order_id, cleaner_id)
    if not result:
        raise HTTPException(status_code=404, detail='Order not found')
    return result
