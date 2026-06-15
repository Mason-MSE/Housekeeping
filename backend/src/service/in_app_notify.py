"""Create in-app notifications; callers must ``commit`` the session."""
from typing import Optional

from sqlalchemy.orm import Session

from model.notification import NotificationModel


def notify_user(
    db: Session,
    user_id: Optional[int],
    title: str,
    content: Optional[str] = None,
    notif_type: str = 'info',
    link_url: Optional[str] = None,
) -> None:
    """Queue one notification row for ``user_id`` (no commit).

    Args:
        db: SQLAlchemy session.
        user_id: Recipient; if missing/0, no-op.
        title: Short title (truncated to match DB column).
        content: Optional body text.
        notif_type: Stored in ``notification.type`` (max 50 chars).
        link_url: Optional path; appended to content (DB has no link_url column).
    """
    if not user_id:
        return
    safe_title = (title or '')[:255]
    safe_type = (notif_type or 'info')[:50]
    body_parts: list[str] = []
    if content and str(content).strip():
        body_parts.append(str(content).strip())
    if link_url and str(link_url).strip():
        body_parts.append(f'Open: {str(link_url).strip()[:500]}')
    merged_content = '\n\n'.join(body_parts) if body_parts else None
    db.add(
        NotificationModel(
            user_id=user_id,
            title=safe_title,
            content=merged_content,
            type=safe_type,
            is_read=0,
        )
    )
