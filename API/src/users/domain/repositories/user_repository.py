from abc import ABC, abstractmethod
from typing import List, Optional
from API.src.users.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[User]:
        """Obtener todos los usuarios"""
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[User]:
        """Buscar usuario por ID"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Buscar usuario por email"""
        pass

    @abstractmethod
    def update(self, id: int, user_data: dict) -> User:
        """Actualizar usuario"""
        pass