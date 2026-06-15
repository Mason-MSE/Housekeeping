from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.role_resource import role_resource
from schemas.role_resource import RoleResourceSchema, RoleResourceCreateSchema, RoleResourceUpdateSchema

import math

# Database session and service dependencies

# Pydantic schemas for request and response validation

# Create API router with prefix and tag
router = APIRouter(prefix='/api/role-resource', tags=['role_resource'])

@router.get('/', response_model=List[RoleResourceSchema])
def read_all(service: role_resource = Depends(get_service(role_resource))):
    """
    Retrieve all records.
    """
    return service.get_all()

@router.get('/{id}', response_model=RoleResourceSchema)
def read_item(id, service: role_resource = Depends(get_service(role_resource))):
    """
    Retrieve a single record by primary key.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=RoleResourceSchema)
def create_item(item_in: RoleResourceCreateSchema, service: role_resource = Depends(get_service(role_resource))):
    """
    Create a new record.
    """
    return service.create(item_in)

@router.put('/{id}', response_model=RoleResourceSchema)
def update_item(id, item_in: RoleResourceUpdateSchema, service: role_resource = Depends(get_service(role_resource))):
    """
    Update an existing record by primary key.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return service.update(db_obj, item_in)

@router.delete('/{id}')
def delete_item(id, service: role_resource = Depends(get_service(role_resource))):
    """
    Delete a record by primary key.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    service.delete(db_obj)
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(pageParam: PaginationRequest, service: role_resource = Depends(get_service(role_resource))):
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
        'items': [RoleResourceSchema.model_validate(item, from_attributes=True) for item in items]
    }
