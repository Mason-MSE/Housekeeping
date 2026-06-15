# Standard library imports
import json
import math
from typing import Any, Dict, List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.booking import booking
from schemas.booking import BookingSchema, BookingCreateSchema, BookingUpdateSchema

# Pydantic schemas for request and response validation


# Create API router with prefix and tag
router = APIRouter(prefix='/api/booking', tags=['booking'])

@router.get('/', response_model=List[BookingSchema])
def read_all(service: booking = Depends(get_service(booking))):
    """
    Retrieve all records.
    """
    return service.get_all()

@router.get('/{booking_id}', response_model=BookingSchema)
def read_item(booking_id,service: booking = Depends(get_service(booking))):
    """
    Retrieve a single record by primary key.
    """
    db_obj = service.get(booking_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=BookingSchema)
def create_item(item_in: BookingCreateSchema,service: booking = Depends(get_service(booking))):
    """
    Create a new record.
    """
    return service.create(item_in)

@router.put('/{booking_id}', response_model=BookingSchema)
def update_item(booking_id, item_in: BookingUpdateSchema, service: booking = Depends(get_service(booking))):
    """
    Update an existing record by primary key.
    """
    db_obj = service.get( booking_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return service.update( db_obj, item_in)

@router.delete('/{booking_id}')
def delete_item(booking_id,service: booking = Depends(get_service(booking))):
    """
    Delete a record by primary key.
    """
    db_obj = service.get( booking_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    service.delete( db_obj)
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(
    pageParam:PaginationRequest,
    service: booking = Depends(get_service(booking))
):
    """
       Paginated list of bookings with optional filters and sorting.
    """
    filter_dict: Dict[str, Any] = {}
    if pageParam.filters:
        try:
            filter_dict =pageParam.filters
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid filters JSON")


    total, items = service.get_paginated(
        page=pageParam.page,
        page_size=pageParam.page_size,
        filters=filter_dict,
        order_by=pageParam.order_by
    )
    return {
        "current_page": pageParam.page,
        "page_total": math.ceil(total / pageParam.page_size),
        "total": total,
        "items": [BookingSchema.model_validate(item, from_attributes=True) for item in items]
}
