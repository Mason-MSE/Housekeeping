from typing import List

from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import require_permission, get_service
from service.order_photo import OrderPhotoService
from model.user import UserModel
from schemas.housekeeping import OrderPhotoSchema, OrderPhotoCreateSchema, ReorderSchema




router = APIRouter(prefix='/api/order-photo', tags=['order-photo'])


@router.get('/order/{order_id}', response_model=List[OrderPhotoSchema])
def get_photos_by_order(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: OrderPhotoService = Depends(get_service(OrderPhotoService))
):
    """Get all photos associated with a specific service order.

    Args:
        order_id: The ID of the service order.
        current_user: Authenticated user.
        service: Injected OrderPhotoService instance.

    Returns:
        List of OrderPhotoSchema objects for the given order.
    """
    return service.get_by_order(order_id)


@router.post('/', response_model=OrderPhotoSchema)
def create_photo(
    photo_in: OrderPhotoCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    service: OrderPhotoService = Depends(get_service(OrderPhotoService))
):
    """Upload a new photo for a service order.

    Args:
        photo_in: Photo data including order_id, photo_type, and photo_data (base64).
        current_user: Authenticated user.
        service: Injected OrderPhotoService instance.

    Returns:
        The created OrderPhotoSchema object.
    """
    return service.create(photo_in, current_user.id)


@router.post('/reorder')
def reorder_photos(
    reorder_data: ReorderSchema,
    current_user: UserModel = Depends(require_permission()),
    service: OrderPhotoService = Depends(get_service(OrderPhotoService))
):
    """Reorder photos for a service order by providing an ordered list of photo IDs.

    Args:
        reorder_data: Schema containing the ordered list of photo_ids.
        current_user: Authenticated user.
        service: Injected OrderPhotoService instance.

    Returns:
        dict indicating success.
    """
    return service.reorder_photos(list(reorder_data.photo_ids))


@router.delete('/{photo_id}')
def delete_photo(
    photo_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: OrderPhotoService = Depends(get_service(OrderPhotoService))
):
    """Delete a photo by its ID.

    Args:
        photo_id: The ID of the photo to delete.
        current_user: Authenticated user.
        service: Injected OrderPhotoService instance.

    Returns:
        dict with success status.
    """
    result = service.delete(photo_id)
    if not result:
        raise HTTPException(status_code=404, detail='Photo not found')
    return {'ok': True}
