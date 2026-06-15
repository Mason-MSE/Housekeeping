from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.user_role import user_role
from schemas.user_role import UserRoleSchema, UserRoleCreateSchema, UserRoleUpdateSchema

import math

# Database session and service dependencies

# Pydantic schemas for request and response validation

# Create API router with prefix and tag
router = APIRouter(prefix='/api/user-role', tags=['user_role'])

@router.get('/', response_model=List[UserRoleSchema])
def read_all(service: user_role = Depends(get_service(user_role))):
    """
    Retrieve all records.
    """
    return service.get_all()

@router.get('/{user_id}/{role_id}', response_model=UserRoleSchema)
def read_item(user_id, role_id, service: user_role = Depends(get_service(user_role))):
    """
    Retrieve a single record by primary key.
    """
    db_obj = service.get(user_id, role_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=UserRoleSchema)
def create_item(item_in: UserRoleCreateSchema, service: user_role = Depends(get_service(user_role))):
    """
    Create a new record.
    """
    return service.create(item_in)

@router.put('/{user_id}/{role_id}', response_model=UserRoleSchema)
def update_item(user_id, role_id, item_in: UserRoleUpdateSchema, service: user_role = Depends(get_service(user_role))):
    """
    Update an existing record by primary key.
    """
    db_obj = service.get(user_id, role_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return service.update(db_obj, item_in)

@router.delete('/{user_id}/{role_id}')
def delete_item(user_id, role_id, service: user_role = Depends(get_service(user_role))):
    """
    Delete a record by primary key.
    """
    db_obj = service.get(user_id, role_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    service.delete(db_obj)
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(pageParam: PaginationRequest, service: user_role = Depends(get_service(user_role))):
    """
    Paginated list of records with optional filters and sorting.
    """
    filter_dict: Dict[str, Any] = {}
    if pageParam.filters:
        try:
            filter_dict = pageParam.filters
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid filters JSON")

    total, items = service.get_paginated(
        page=pageParam.page,
        page_size=pageParam.page_size,
        filters=filter_dict,
        order_by=pageParam.order_by
    )
    return {
        'current_page': pageParam.page,
        'page_total': math.ceil(total / pageParam.page_size),
        'total': total,
        'items': [UserRoleSchema.model_validate(item, from_attributes=True) for item in items]
    }
