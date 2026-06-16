from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.role import role
from schemas.role import RoleSchema, RoleCreateSchema, RoleUpdateSchema

import math

router = APIRouter(prefix='/api/role', tags=['role'])

@router.get('/', response_model=List[RoleSchema])
def read_all(service: role = Depends(get_service(role))):
    """Retrieve all role records.

    Args:
        service: Injected role service instance.

    Returns:
        List of RoleSchema objects.
    """
    return service.get_all()

@router.get('/{id}', response_model=RoleSchema)
def read_item(id: int, service: role = Depends(get_service(role))):
    """Retrieve a single role record by primary key.

    Args:
        id: The role ID.
        service: Injected role service instance.

    Returns:
        RoleSchema object.

    Raises:
        HTTPException 404: If the role is not found.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=RoleSchema)
def create_item(item_in: RoleCreateSchema, service: role = Depends(get_service(role))):
    """Create a new role record.

    Args:
        item_in: Role creation data.
        service: Injected role service instance.

    Returns:
        The created RoleSchema object.

    Raises:
        HTTPException 400: If creation fails (e.g. duplicate role name).
    """
    try:
        return service.create(item_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.put('/{id}', response_model=RoleSchema)
def update_item(id: int, item_in: RoleUpdateSchema, service: role = Depends(get_service(role))):
    """Update an existing role record by primary key.

    Args:
        id: The role ID.
        item_in: Role update data (partial).
        service: Injected role service instance.

    Returns:
        The updated RoleSchema object.

    Raises:
        HTTPException 404: If the role is not found.
        HTTPException 400: If update fails.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    try:
        return service.update(db_obj, item_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.delete('/{id}')
def delete_item(id: int, service: role = Depends(get_service(role))):
    """Delete a role record by primary key (soft delete).

    Args:
        id: The role ID.
        service: Injected role service instance.

    Returns:
        dict with success status.

    Raises:
        HTTPException 404: If the role is not found.
        HTTPException 400: If deletion fails.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    try:
        service.delete(db_obj)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(pageParam: PaginationRequest, service: role = Depends(get_service(role))):
    """Paginated list of role records with optional filters and sorting.

    Args:
        pageParam: Pagination parameters including page, page_size, filters, and order_by.
        service: Injected role service instance.

    Returns:
        dict with current_page, page_total, total, and items (list of RoleSchema).
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
        'items': [RoleSchema.model_validate(item, from_attributes=True) for item in items]
    }
