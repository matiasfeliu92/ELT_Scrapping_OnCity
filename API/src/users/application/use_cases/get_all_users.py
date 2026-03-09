from typing import List
from API.src.users.domain.entities.user import User
from API.src.users.domain.repositories.user_repository import UserRepository


class GetAllUsers:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self) -> List[User]:
        return self.repo.find_all()