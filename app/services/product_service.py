from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.nursery import Nursery
from app.schemas.product_schema import ProductCreateRequest
from app.utils.product_id_generator import generate_product_id_8digit

EMPLOYEE_FIXED_RATE_PERCENT = 2.25


def add_product_service(
    db: Session,
    payload: ProductCreateRequest,
    *,
    actor_role: str,
    merge_existing_inventory: bool = False,
):
    nursery = db.query(Nursery).filter(Nursery.nursery_id == payload.nursery_id).first()
    if not nursery:
        raise HTTPException(status_code=404, detail="Nursery not found")

    product_id = generate_product_id_8digit(payload.nursery_id, payload.size, payload.item_name)

    existing = db.query(Product).filter(Product.product_id == product_id).first()
    if existing:
        if merge_existing_inventory:
            existing.inventory_quantity = existing.inventory_quantity + payload.inventory_quantity
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(
            status_code=409,
            detail=f"Product already exists with product_id={product_id}"
        )

    effective_rate = payload.rate_percentage
    if actor_role == "employee":
        effective_rate = EMPLOYEE_FIXED_RATE_PERCENT

    new_product = Product(
        product_id=product_id,
        nursery_id=payload.nursery_id,
        item_name=payload.item_name.strip(),
        size=payload.size.strip(),
        inventory_quantity=payload.inventory_quantity,
        ordered_quantity=payload.ordered_quantity,
        base_price_per_unit=payload.base_price_per_unit,
        rate_percentage=effective_rate,
        image_url=str(payload.image_url) if payload.image_url else None
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def add_stock_service(db: Session, product_id: str, quantity: int) -> Product:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.inventory_quantity = product.inventory_quantity + quantity
    db.commit()
    db.refresh(product)
    return product
