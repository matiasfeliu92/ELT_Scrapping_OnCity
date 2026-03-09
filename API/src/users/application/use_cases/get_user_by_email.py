from typing import List

from API.src.users.domain.entities.user import User
from API.src.users.domain.repositories.user_repository import UserRepository


class GetUserByEmail:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self, email: str) -> User:
        user = self.repo.find_by_email(email)
        if not user:
            raise ValueError(f"Usuario con email {email} no encontrado")
        return user