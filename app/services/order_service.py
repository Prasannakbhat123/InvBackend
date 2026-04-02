from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from uuid import uuid4
from decimal import Decimal

from app.models.order_table import OrderTable
from app.models.ordered_products import OrderedProducts
from app.models.product import Product
from app.models.user import UserTable

from app.schemas.order_schema import (
    OrderCreateRequest,
    OrderAddProductRequest,
    OrderRemoveProductRequest,
)

from app.utils.order_calc import calculate_line_total
from app.core.id_generator import generate_order_id


#ALLOWED_EDIT_STATUSES = {"CREATED", "IN_PROGRESS"}
EDITABLE_STATUS = "CREATED"


def _refresh_order_total(db: Session, order_id: str) -> Decimal:
    total = db.query(func.coalesce(func.sum(OrderedProducts.total_price), 0)) \
              .filter(OrderedProducts.order_id == order_id) \
              .scalar()

    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    order.total_order_amount = total
    order.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return total


def create_order_service(db: Session, payload: OrderCreateRequest) -> OrderTable:
    user = db.query(UserTable).filter(UserTable.user_id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_order_id = generate_order_id(db)
    
    new_order = OrderTable(
        order_id=new_order_id,
        user_id=payload.user_id,
        client_name=payload.client_name.strip(),
        total_order_amount=0,
        status="CREATED"  
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


def add_product_to_order_service(db: Session, order_id: str, payload: OrderAddProductRequest):
    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != EDITABLE_STATUS:
        raise HTTPException(status_code=400, detail=f"Cannot modify order in status={order.status}")

    product = db.query(Product).filter(Product.product_id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    line = db.query(OrderedProducts).filter(
        OrderedProducts.order_id == order_id,
        OrderedProducts.product_id == payload.product_id
    ).first()

    old_qty = line.quantity if line else 0
    new_qty = payload.quantity

    delta = new_qty - old_qty

    # available stock = inventory - reserved
    available = product.inventory_quantity - product.ordered_quantity

    if delta > 0 and delta > available:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available={available}, Requested Increase={delta}"
        )

    line_total = calculate_line_total(
        quantity=new_qty,
        unit_price=Decimal(payload.unit_price),
        rate_percentage=Decimal(payload.rate_percentage) if payload.rate_percentage is not None else None
    )

    if line:
        line.quantity = new_qty
        line.unit_price = payload.unit_price
        line.rate_percentage = payload.rate_percentage
        line.total_price = line_total
    else:
        line = OrderedProducts(
            order_id=order_id,
            product_id=payload.product_id,
            quantity=new_qty,
            unit_price=payload.unit_price,
            rate_percentage=payload.rate_percentage,
            total_price=line_total
        )
        db.add(line)

    # update reserved stock
    product.ordered_quantity += delta

    if product.ordered_quantity < 0:
        raise HTTPException(status_code=500, detail="Stock reservation became negative")

    db.commit()

    order_total = _refresh_order_total(db, order_id)
    return line, order_total


# Remove/decrement product from order + rollback ordered_quantity
def remove_product_from_order_service(db: Session, order_id: str, payload: OrderRemoveProductRequest):
    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != EDITABLE_STATUS:
        raise HTTPException(status_code=400, detail=f"Cannot modify order in status={order.status}")

    line = db.query(OrderedProducts).filter(
        OrderedProducts.order_id == order_id,
        OrderedProducts.product_id == payload.product_id
    ).first()

    if not line:
        raise HTTPException(status_code=404, detail="Product not found in this order")

    product = db.query(Product).filter(Product.product_id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    old_qty = line.quantity

    # remove whole line
    if payload.quantity is None or payload.quantity >= old_qty:
        removed_qty = old_qty
        db.delete(line)

    # decrement quantity
    else:
        removed_qty = payload.quantity
        line.quantity = old_qty - removed_qty

        line.total_price = calculate_line_total(
            quantity=line.quantity,
            unit_price=Decimal(line.unit_price),
            rate_percentage=Decimal(line.rate_percentage) if line.rate_percentage is not None else None
        )

    # rollback reserved stock
    product.ordered_quantity -= removed_qty

    if product.ordered_quantity < 0:
        raise HTTPException(status_code=500, detail="Stock reservation became negative")

    db.commit()

    order_total = _refresh_order_total(db, order_id)
    return order_total

def update_order_basic_details_service(db: Session, order_id: str, client_name: str | None = None):
    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != EDITABLE_STATUS:
        raise HTTPException(status_code=400, detail="Order can be updated only when status is CREATED")
    if client_name is not None:
        order.client_name = client_name.strip()

    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order