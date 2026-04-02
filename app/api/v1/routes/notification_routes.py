from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.core.deps import get_db, require_admin
from app.models.product import Product
from app.models.notification import Notification
from app.models.user import UserTable
from pydantic import BaseModel

router = APIRouter()

class LowStockNotification(BaseModel):
    product_id: str
    item_name: str
    size: str
    current_stock: int
    threshold: int
    nursery_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminNotification(BaseModel):
    notification_id: str
    type: str
    title: str
    message: str
    actor_user_id: str | None = None
    reference_id: str | None = None
    created_at: datetime

@router.get("/low-stock", response_model=List[LowStockNotification])
def get_low_stock_items(
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(require_admin)
):
    """
    Get all products with inventory below their low stock threshold (Admin only)
    """
    low_stock_products = db.query(Product).filter(
        Product.inventory_quantity <= Product.low_stock_threshold
    ).all()
    
    notifications = [
        LowStockNotification(
            product_id=product.product_id,
            item_name=product.item_name,
            size=product.size,
            current_stock=product.inventory_quantity,
            threshold=product.low_stock_threshold,
            nursery_id=product.nursery_id,
            created_at=datetime.now(timezone.utc),
        )
        for product in low_stock_products
    ]
    
    return notifications


@router.get("", response_model=List[AdminNotification])
def get_admin_notifications(
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(require_admin),
):
    notifications = (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        AdminNotification(
            notification_id=item.notification_id,
            type=item.type,
            title=item.title,
            message=item.message,
            actor_user_id=item.actor_user_id,
            reference_id=item.reference_id,
            created_at=item.created_at,
        )
        for item in notifications
    ]
