import uuid
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    *,
    type: str,
    title: str,
    message: str,
    actor_user_id: str | None = None,
    reference_id: str | None = None,
) -> Notification:
    notification = Notification(
        notification_id=f"ntf_{uuid.uuid4().hex[:16]}",
        type=type,
        title=title,
        message=message,
        actor_user_id=actor_user_id,
        reference_id=reference_id,
    )
    db.add(notification)
    db.flush()
    return notification
