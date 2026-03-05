from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Product:
    id: int                # Agregamos el ID numérico para referencia única
    product_id: str
    name: str
    brand: str
    main_category: str
    sub_category: str
    list_price: Optional[float]
    cash_price: Optional[float]
    stock_level: int
    is_active: bool
    updated_at: datetime
    retailer: str
    link: str