from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from API.src.products.domain.entities.product import Product as ProductDomain
from API.src.products.domain.repositories.product_repository import ProductRepository
from API.src.products.infrastructure.models.product import Product as ProductModel


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def _map_model_to_entity(self, model: ProductModel) -> ProductDomain:
        return ProductDomain(
            id=model.id,
            product_id=model.product_id,
            brand=model.brand,
            name=model.name,
            main_category=model.main_category,
            sub_category=model.sub_category,
            list_price=model.list_price,
            cash_price=model.cash_price,
            stock_level=model.stock_level,
            is_active=model.is_active,
            updated_at=model.updated_at,
            retailer=model.retailer,
            link=model.link
        )
    
    def get_all(self) -> List[ProductDomain]:
        orm_products = self.session.query(
            ProductModel.id, 
            ProductModel.product_id, 
            ProductModel.brand, 
            ProductModel.name, 
            ProductModel.main_category, 
            ProductModel.sub_category, 
            ProductModel.list_price, 
            ProductModel.cash_price, 
            ProductModel.stock_level, 
            ProductModel.is_active, 
            ProductModel.updated_at,
            ProductModel.retailer,
            ProductModel.link
        ).filter(
            ProductModel.is_active == True
        ).order_by(
            func.right(ProductModel.product_id, 3).asc()
        ).all()
        return [self._map_model_to_entity(product) for product in orm_products]
    
    def get_by_id(self, id: int) -> Optional[ProductDomain]:
        orm_product = self.session.query(
            ProductModel.id, 
            ProductModel.product_id, 
            ProductModel.brand, 
            ProductModel.name, 
            ProductModel.main_category, 
            ProductModel.sub_category, 
            ProductModel.list_price, 
            ProductModel.cash_price, 
            ProductModel.stock_level, 
            ProductModel.is_active, 
            ProductModel.updated_at,
            ProductModel.retailer,
            ProductModel.link
        ).filter(
            ProductModel.id == id
        ).one_or_none()
        if orm_product is None:
            return None
        return self._map_model_to_entity(orm_product)