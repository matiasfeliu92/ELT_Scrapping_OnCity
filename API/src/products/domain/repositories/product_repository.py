from abc import ABC, abstractmethod
from typing import List, Optional

from API.src.products.domain.entities.product import Product

class ProductRepository(ABC):
    """Abstract repository interface for `Product` domain entity.

    Implementations live in the infrastructure layer and must translate
    between persistence models and the domain `Product` entity.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Return a list of all available products"""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Product]:
        """Return a product by id or `None` if not found."""
