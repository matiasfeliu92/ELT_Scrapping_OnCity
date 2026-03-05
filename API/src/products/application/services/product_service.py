from typing import List

from API.src.products.application.use_cases.get_all_products import GetAllProducts
from API.src.products.application.use_cases.get_product_by_id import GetProductById
from API.src.products.domain.entities.product import Product as ProductDomain
from API.src.products.domain.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo
        self.get_all_products = GetAllProducts(self.repo)
        self.get_product_by_id = GetProductById(self.repo)

    def get_all(self) -> List[ProductDomain]:
        return self.get_all_products.__call__()
    
    def get_one_by_id(self, id:int) -> ProductDomain:
        return self.get_product_by_id.__call__(id)