from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import UserTable
from app.schemas.product_schema import (
    ProductCreateRequest,
    ProductCreateResponse,
    ProductAddStockRequest,
    ProductAddStockResponse,
)
from app.services.notification_service import create_notification
from app.services.product_service import (
    add_product_service,
    add_stock_service,
    EMPLOYEE_FIXED_RATE_PERCENT,
)

router = APIRouter()

@router.post("/add", response_model=ProductCreateResponse)
def add_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(get_current_user)
):
    if current_user.role not in ["admin", "employee"]:
        raise HTTPException(status_code=403, detail="Access denied")

    is_employee = current_user.role == "employee"
    product = add_product_service(
        db,
        payload,
        actor_role=current_user.role,
        merge_existing_inventory=is_employee,
    )

    if is_employee:
        create_notification(
            db,
            type="inventory_update",
            title="Inventory Updated By Employee",
            message=(
                f"{current_user.user_username} added/updated product {product.item_name} "
                f"({product.product_id}) with fixed rate {EMPLOYEE_FIXED_RATE_PERCENT}%"
            ),
            actor_user_id=current_user.user_id,
            reference_id=product.product_id,
        )
        db.commit()

    return ProductCreateResponse(
        product_id=product.product_id,
        message="Product added successfully "
    )


@router.patch("/{product_id}/add-stock", response_model=ProductAddStockResponse)
def add_product_stock(
    product_id: str,
    payload: ProductAddStockRequest,
    db: Session = Depends(get_db),
    current_user: UserTable = Depends(get_current_user),
):
    if current_user.role not in ["admin", "employee"]:
        raise HTTPException(status_code=403, detail="Access denied")

    product = add_stock_service(db, product_id, payload.quantity)

    if current_user.role == "employee":
        create_notification(
            db,
            type="inventory_update",
            title="Inventory Increased By Employee",
            message=(
                f"{current_user.user_username} added {payload.quantity} units to "
                f"{product.item_name} ({product.product_id})"
            ),
            actor_user_id=current_user.user_id,
            reference_id=product.product_id,
        )
        db.commit()

    return ProductAddStockResponse(
        product_id=product.product_id,
        added_quantity=payload.quantity,
        inventory_quantity=product.inventory_quantity,
        message="Stock updated successfully",
    )
