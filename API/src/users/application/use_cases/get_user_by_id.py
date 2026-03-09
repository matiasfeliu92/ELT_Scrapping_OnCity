from typing import List

from API.src.users.domain.entities.user import User
from API.src.users.domain.repositories.user_repository import UserRepository
from API.src.shared.exceptions import NotFoundError

class GetUserById:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def __call__(self, id: int) -> User:
        user = self.repo.find_by_id(id)
        if not user:
            raise NotFoundError(f"User with id={id} not found")
        return user