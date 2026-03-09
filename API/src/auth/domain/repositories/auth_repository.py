from abc import ABC, abstractmethod
from typing import Optional

from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.entities.auth_user import AuthUser


class AuthRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[AuthUser]:
        pass

    @abstractmethod
    def create_user(self, credentials: AuthCredentials) -> AuthUser:
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        pass

    @abstractmethod
    def generate_access_token(self, user: AuthUser) -> str:
        pass

    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        pass

    @abstractmethod
    def persist_token(self, user_id: int, token: str) -> None:
        pass
