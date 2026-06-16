from typing import Optional

from sqlalchemy.orm import Session

from model.notification import NotificationModel

import math


class NotificationService:
    def __init__(self, db: Session):
        """Initialize the notification service with a database session."""
        self.db = db

    def get_notifications_paginated(self, user_id: int, page: int = 1, page_size: int = 10, type: str = None, is_read: int = None, title: str = None):
        """Retrieve paginated notifications for a user with optional filters."""
        query = self.db.query(NotificationModel).filter(NotificationModel.user_id == user_id)

        if type:
            query = query.filter(NotificationModel.type == type)
        if is_read is not None:
            query = query.filter(NotificationModel.is_read == is_read)
        if title:
            query = query.filter(NotificationModel.title.like(f'%{title}%'))

        total = query.count()
        items = query.order_by(NotificationModel.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "current_page": page,
            "page_total": math.ceil(total / page_size) if page_size > 0 else 0,
            "total": total,
            "items": items
        }

    def get_notifications(self, user_id: int, unread_only: bool = False):
        """Retrieve recent notifications for a user, optionally only unread ones."""
        query = self.db.query(NotificationModel).filter(NotificationModel.user_id == user_id)
        if unread_only:
            query = query.filter(NotificationModel.is_read == 0)
        return query.order_by(NotificationModel.create_time.desc()).limit(50).all()

    def get_unread_count(self, user_id: int):
        """Return the count of unread notifications for a user."""
        count = self.db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == 0
        ).count()
        return {'count': count}

    def mark_as_read(self, user_id: int, notification_id: int):
        """Mark a specific notification as read."""
        notification = self.db.query(NotificationModel).filter(
            NotificationModel.id == notification_id,
            NotificationModel.user_id == user_id
        ).first()
        if not notification:
            return {"error": "Notification not found", "status_code": 404}
        notification.is_read = 1
        self.db.commit()
        return {'ok': True}

    def mark_all_as_read(self, user_id: int):
        """Mark all unread notifications for a user as read."""
        self.db.query(NotificationModel).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == 0
        ).update({'is_read': 1})
        self.db.commit()
        return {'ok': True}

    def delete_notification(self, user_id: int, notification_id: int):
        """Delete a specific notification."""
        notification = self.db.query(NotificationModel).filter(
            NotificationModel.id == notification_id,
            NotificationModel.user_id == user_id
        ).first()
        if not notification:
            return {"error": "Notification not found", "status_code": 404}
        self.db.delete(notification)
        self.db.commit()
        return {'ok': True}

    def create_notification(self, user_id: int, title: str, content: str = None, type: str = 'info', link_url: str = None):
        """Create and persist a new notification for a user."""
        body_parts: list[str] = []
        if content and str(content).strip():
            body_parts.append(str(content).strip())
        if link_url and str(link_url).strip():
            body_parts.append(f'Open: {str(link_url).strip()[:500]}')
        merged = '\n\n'.join(body_parts) if body_parts else None
        notification = NotificationModel(
            user_id=user_id,
            title=title,
            content=merged,
            type=type,
            is_read=0,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
