from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.dependencies import get_current_user, require_permission, get_service
from database import get_db
from service.service_order import ServiceOrderService
from model.user import UserModel
from schemas.housekeeping import ServiceOrderSchema, ServiceOrderCreateSchema, RateSchema
from schemas.PaginationRequest import PaginationRequest

import math



router = APIRouter(prefix='/api/service-order', tags=['service-order'])


def get_user_roles(user_id: int, db: Session):
    """Helper function to get user roles"""
    from model.role import RoleModel
    from model.user_role import UserRoleModel
    roles = db.query(RoleModel.role_name).join(
        UserRoleModel, UserRoleModel.role_id == RoleModel.id
    ).filter(UserRoleModel.user_id == user_id).all()
    return [r[0] for r in roles] if roles else []


@router.get('/', response_model=List[ServiceOrderSchema])
def read_all(
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService)),
    db: Session = Depends(get_db)
):
    user_roles = get_user_roles(current_user.id, db)
    user_id = current_user.id

    if any(r in ["admin", "manager"] for r in user_roles):
        return service.get_all()
    elif any(r in ["cleaner", "staff", "employee"] for r in user_roles):
        return service.get_by_cleaner(user_id)
    else:
        return service.get_by_guest(user_id)


@router.get('/{order_id}', response_model=ServiceOrderSchema)
def read_item(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService)),
    db: Session = Depends(get_db)
):
    order = service.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    user_roles = get_user_roles(current_user.id, db)
    if not any(r in ["admin", "cleaner"] for r in user_roles) and order.guest_id != current_user.id:
        raise HTTPException(status_code=403, detail='Access denied')
    return order


@router.post('/', response_model=ServiceOrderSchema)
def create_item(
    item_in: ServiceOrderCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    return service.create(item_in, current_user.id)


@router.put('/{order_id}', response_model=ServiceOrderSchema)
def update_item(
    order_id: int,
    item_in: dict,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can modify orders')
    order = service.update(order_id, item_in)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


@router.delete('/{order_id}')
def delete_item(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can delete orders')
    result = service.delete(order_id)
    if not result:
        raise HTTPException(status_code=404, detail='Order not found')
    return {'ok': True}


@router.post('/assign/{order_id}')
def assign_staff(
    order_id: int,
    staff_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admin can assign staff to orders')
    order = service.assign_staff(order_id, staff_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


@router.post('/start/{order_id}')
def start_work(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    order = service.start_work(order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


@router.post('/complete/{order_id}')
def complete_work(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    order = service.complete(order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


@router.post('/upload-photo/{order_id}')
def upload_photo(
    order_id: int,
    photo_type: str,
    photo_data: str,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    order = service.upload_photo(order_id, photo_type, photo_data)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


@router.post('/cancel/{order_id}')
def cancel_order(
    order_id: int,
    reason: str = None,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    order = service.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    if current_user.role != 'admin' and order.guest_id != current_user.id:
        raise HTTPException(status_code=403, detail='Only admin or the customer who created the order can cancel')
    result = service.cancel_order(order_id, reason)
    if not result:
        raise HTTPException(status_code=404, detail='Order not found')
    return result


@router.post('/rate/{order_id}')
def rate_order(
    order_id: int,
    rate_data: RateSchema,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService))
):
    order = service.rate_order(order_id, rate_data.rating, rate_data.comment)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order


@router.post('/paginated')
def read_paginated(
    pageParam: PaginationRequest,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceOrderService = Depends(get_service(ServiceOrderService)),
    db: Session = Depends(get_db)
):
    filter_dict: Dict[str, Any] = {}
    if pageParam.filters:
        filter_dict = pageParam.filters

    user_roles = get_user_roles(current_user.id, db)
    user_id = current_user.id

    if any(r in ["admin", "manager"] for r in user_roles):
        total, items = service.get_paginated(
            page=pageParam.page,
            page_size=pageParam.page_size,
            filters=filter_dict,
            order_by=pageParam.order_by
        )
    elif any(r in ["cleaner", "staff", "employee"] for r in user_roles):
        filter_dict["cleaner_id"] = user_id
        total, items = service.get_paginated(
            page=pageParam.page,
            page_size=pageParam.page_size,
            filters=filter_dict,
            order_by=pageParam.order_by
        )
    else:
        filter_dict["guest_id"] = user_id
        total, items = service.get_paginated(
            page=pageParam.page,
            page_size=pageParam.page_size,
            filters=filter_dict,
            order_by=pageParam.order_by
        )
    return {
        "current_page": pageParam.page,
        "page_total": math.ceil(total / pageParam.page_size) if pageParam.page_size > 0 else 0,
        "total": total,
        "items": items
    }
