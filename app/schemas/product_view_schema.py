from pydantic import BaseModel
from typing import Optional

class ProductView(BaseModel):
    product_id: str
    nursery_id: str
    item_name: str
    size: str
    inventory_quantity: int
    ordered_quantity: int
    base_price_per_unit: str
    rate_percentage: str
    image_url: Optional[str] = None
