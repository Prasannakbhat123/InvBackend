from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.product import Product
from app.schemas.product_view_schema import ProductView

router = APIRouter()

@router.get("/all", response_model=list[ProductView])
def show_all_products(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    products = db.query(Product).all()
    return [
        ProductView(
            product_id=p.product_id,
            nursery_id=p.nursery_id,
            item_name=p.item_name,
            size=p.size,
            inventory_quantity=p.inventory_quantity,
            ordered_quantity=p.ordered_quantity,
            base_price_per_unit=str(p.base_price_per_unit),
            rate_percentage=str(p.rate_percentage),
            image_url=p.image_url,
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductView)
def show_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductView(
        product_id=product.product_id,
        nursery_id=product.nursery_id,
        item_name=product.item_name,
        size=product.size,
        inventory_quantity=product.inventory_quantity,
        ordered_quantity=product.ordered_quantity,
        base_price_per_unit=str(product.base_price_per_unit),
        rate_percentage=str(product.rate_percentage),
        image_url=product.image_url
    )
