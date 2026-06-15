from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.dependencies import get_current_user, require_permission, get_service
from service.notification import NotificationService
from model.user import UserModel
from schemas.housekeeping import NotificationSchema, NotificationCreateSchema




router = APIRouter(prefix='/api/notification', tags=['notification'])


@router.get('/paginated')
def get_notifications_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None),
    is_read: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_permission()),
    service: NotificationService = Depends(get_service(NotificationService))
):
    result = service.get_notifications_paginated(
        current_user.id,
        page=page,
        page_size=page_size,
        type=type,
        is_read=is_read,
        title=title
    )
    result["items"] = [NotificationSchema.model_validate(item, from_attributes=True) for item in result["items"]]
    return result


@router.get('/', response_model=List[NotificationSchema])
def get_notifications(
    unread_only: bool = False,
    current_user: UserModel = Depends(require_permission()),
    service: NotificationService = Depends(get_service(NotificationService))
):
    notifications = service.get_notifications(current_user.id, unread_only)
    return notifications


@router.get('/unread-count')
def get_unread_count(
    current_user: UserModel = Depends(require_permission()),
    service: NotificationService = Depends(get_service(NotificationService))
):
    return service.get_unread_count(current_user.id)


@router.post('/{notification_id}/read')
def mark_as_read(
    notification_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: NotificationService = Depends(get_service(NotificationService))
):
    result = service.mark_as_read(current_user.id, notification_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.post('/read-all')
def mark_all_as_read(
    current_user: UserModel = Depends(require_permission()),
    service: NotificationService = Depends(get_service(NotificationService))
):
    return service.mark_all_as_read(current_user.id)


@router.delete('/{notification_id}')
def delete_notification(
    notification_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: NotificationService = Depends(get_service(NotificationService))
):
    result = service.delete_notification(current_user.id, notification_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.post('/create')
def create_notification(
    notification_in: NotificationCreateSchema,
    service: NotificationService = Depends(get_service(NotificationService))
):
    return service.create_notification(
        user_id=notification_in.user_id,
        title=notification_in.title,
        content=notification_in.content,
        type=notification_in.type,
        link_url=notification_in.link_url
    )
