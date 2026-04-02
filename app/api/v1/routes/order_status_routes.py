from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin, get_current_user
from app.models.user import UserTable
from app.services.notification_service import create_notification
from app.services.order_status_service import start_order_service, complete_order_service

router = APIRouter()

# CREATED -> IN_PROGRESS
@router.patch("/{order_id}/start")
def start_order(
    order_id: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    order = start_order_service(db, order_id)
    return {
        "message": "Order moved to IN_PROGRESS ✅",
        "order_id": order.order_id,
        "status": order.status,
        "updated_at": str(order.updated_at)
    }


# IN_PROGRESS -> COMPLETED (accessible by any authenticated user, including employees)
@router.patch("/{order_id}/complete")
def complete_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    order = complete_order_service(db, order_id)

    if current_user.role == "employee":
        create_notification(
            db,
            type="order_completed",
            title="Order Completed By Employee",
            message=(
                f"{current_user.user_username} marked order {order.order_id} as COMPLETED"
            ),
            actor_user_id=current_user.user_id,
            reference_id=order.order_id,
        )
        db.commit()

    return {
        "message": "Order moved to COMPLETED ✅",
        "order_id": order.order_id,
        "status": order.status,
        "updated_at": str(order.updated_at),
        "paid_at": str(order.paid_at)
    }
