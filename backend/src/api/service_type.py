from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import require_permission, get_service
from service.service_type import ServiceTypeService
from model.user import UserModel
from schemas.housekeeping import ServiceTypeSchema, ServiceTypeCreateSchema




router = APIRouter(prefix='/api/service-type', tags=['service-type'])


@router.get('/', response_model=List[ServiceTypeSchema])
def get_all(
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    """Retrieve all service type records.

    Args:
        current_user: Authenticated user.
        service: Injected ServiceTypeService instance.

    Returns:
        List of ServiceTypeSchema objects.
    """
    return service.get_all()


@router.get('/{type_id}', response_model=ServiceTypeSchema)
def get_item(
    type_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    """Retrieve a single service type record by its ID.

    Args:
        type_id: The service type ID.
        current_user: Authenticated user.
        service: Injected ServiceTypeService instance.

    Returns:
        ServiceTypeSchema object.

    Raises:
        HTTPException 404: If the service type is not found.
    """
    item = service.get(type_id)
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return item


@router.post('/', response_model=ServiceTypeSchema)
def create_item(
    item_in: ServiceTypeCreateSchema,
    _auth: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    """Create a new service type record.

    Args:
        item_in: Service type creation data (type_name, description, price, market_price).
        _auth: Authenticated user (permission check only).
        service: Injected ServiceTypeService instance.

    Returns:
        The created ServiceTypeSchema object.
    """
    return service.create(
        type_name=item_in.type_name,
        description=item_in.description,
        price=item_in.price,
        market_price=item_in.market_price,
    )


@router.put('/{type_id}', response_model=ServiceTypeSchema)
def update_item(
    type_id: int,
    item_in: dict,
    _auth: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    """Update an existing service type record.

    Args:
        type_id: The service type ID.
        item_in: Partial update data as a dictionary.
        _auth: Authenticated user (permission check only).
        service: Injected ServiceTypeService instance.

    Returns:
        The updated ServiceTypeSchema object.

    Raises:
        HTTPException 404: If the service type is not found.
    """
    item = service.update(type_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return item


@router.delete('/{type_id}')
def delete_item(
    type_id: int,
    _auth: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    """Delete a service type record (soft delete).

    Args:
        type_id: The service type ID.
        _auth: Authenticated user (permission check only).
        service: Injected ServiceTypeService instance.

    Returns:
        dict with success status.

    Raises:
        HTTPException 404: If the service type is not found.
    """
    item = service.delete(type_id)
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return {'ok': True}
