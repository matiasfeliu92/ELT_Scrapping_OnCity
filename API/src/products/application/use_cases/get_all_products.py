from typing import List

from API.src.products.domain.entities.product import Product
from API.src.products.domain.repositories.product_repository import ProductRepository


class GetAllProducts:
    def __init__(self, repo: ProductRepository):
        self.repo = repo
    
    def __call__(self) -> List[Product]:
        return self.repo.get_all()