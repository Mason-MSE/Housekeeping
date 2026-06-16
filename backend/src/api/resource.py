from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.resource import resource
from schemas.resource import ResourceSchema, ResourceCreateSchema, ResourceUpdateSchema

import math

# Database session and service dependencies

# Pydantic schemas for request and response validation

# Create API router with prefix and tag
router = APIRouter(prefix='/api/resource', tags=['resource'])

@router.get('/', response_model=List[ResourceSchema])
def read_all(service: resource = Depends(get_service(resource))):
    """Retrieve all resource records.

    Args:
        service: Injected resource service instance.

    Returns:
        List of ResourceSchema objects.
    """
    return service.get_all()

@router.get('/{id}', response_model=ResourceSchema)
def read_item(id, service: resource = Depends(get_service(resource))):
    """Retrieve a single resource record by primary key.

    Args:
        id: The resource ID.
        service: Injected resource service instance.

    Returns:
        ResourceSchema object.

    Raises:
        HTTPException 404: If the resource is not found.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=ResourceSchema)
def create_item(item_in: ResourceCreateSchema, service: resource = Depends(get_service(resource))):
    """Create a new resource record.

    Args:
        item_in: Resource creation data.
        service: Injected resource service instance.

    Returns:
        The created ResourceSchema object.
    """
    return service.create(item_in)

@router.put('/{id}', response_model=ResourceSchema)
def update_item(id, item_in: ResourceUpdateSchema, service: resource = Depends(get_service(resource))):
    """Update an existing resource record by primary key.

    Args:
        id: The resource ID.
        item_in: Resource update data (partial).
        service: Injected resource service instance.

    Returns:
        The updated ResourceSchema object.

    Raises:
        HTTPException 404: If the resource is not found.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return service.update(db_obj, item_in)

@router.delete('/{id}')
def delete_item(id, service: resource = Depends(get_service(resource))):
    """Delete a resource record by primary key.

    Args:
        id: The resource ID.
        service: Injected resource service instance.

    Returns:
        dict with success status.

    Raises:
        HTTPException 404: If the resource is not found.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    service.delete(db_obj)
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(pageParam: PaginationRequest, service: resource = Depends(get_service(resource))):
    """Paginated list of resource records with optional filters and sorting.

    Args:
        pageParam: Pagination parameters including page, page_size, filters, and order_by.
        service: Injected resource service instance.

    Returns:
        dict with current_page, page_total, total, and items (list of ResourceSchema).
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
        'items': [ResourceSchema.model_validate(item, from_attributes=True) for item in items]
    }
