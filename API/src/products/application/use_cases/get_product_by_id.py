from typing import List

from API.src.products.domain.entities.product import Product
from API.src.products.domain.repositories.product_repository import ProductRepository
from API.src.shared.exceptions import NotFoundError


class GetProductById:
    def __init__(self, repo: ProductRepository):
        self.repo = repo
    
    def __call__(self, id: int) -> Product:
        id_vo = id
        product = self.repo.get_by_id(id_vo)
        if product is None:
            raise NotFoundError(f"Product with id={id} not found")
        return product