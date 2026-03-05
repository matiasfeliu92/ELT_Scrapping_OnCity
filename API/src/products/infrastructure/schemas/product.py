from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: str
    name: Optional[str]
    brand: Optional[str]
    main_category: Optional[str]
    sub_category: Optional[str]
    list_price: Optional[float]
    cash_price: Optional[float]
    stock_level: int
    is_active: bool
    updated_at: datetime
    retailer: str
    link: str