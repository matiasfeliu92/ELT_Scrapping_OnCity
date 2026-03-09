from typing import List

from API.src.users.application.use_cases.get_all_users import GetAllUsers
from API.src.users.application.use_cases.get_user_by_email import GetUserByEmail
from API.src.users.application.use_cases.get_user_by_id import GetUserById
from API.src.users.application.use_cases.update_user import UpdateUser
from API.src.users.domain.entities.user import User
from API.src.users.domain.repositories.user_repository import UserRepository
from API.src.shared.exceptions import AppException, InternalServerError


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        self._get_all_users = GetAllUsers(repo)
        self._get_user_by_id = GetUserById(repo)
        self._get_user_by_email = GetUserByEmail(repo)
        self._update_user = UpdateUser(repo)

    def get_all(self) -> List[User]:
        """Obtener todos los usuarios"""
        try:
            return self._get_all_users()
        except AppException:
            raise
        except Exception as exc:
            raise InternalServerError("Error obteniendo usuarios") from exc

    def get_by_id(self, id: int) -> User:
        """Obtener usuario por ID"""
        try:
            return self._get_user_by_id(id)
        except AppException:
            raise
        except Exception as exc:
            raise InternalServerError("Error obteniendo usuario por ID") from exc

    def get_by_email(self, email: str) -> User:
        """Obtener usuario por email"""
        try:
            return self._get_user_by_email(email)
        except AppException:
            raise
        except Exception as exc:
            raise InternalServerError("Error obteniendo usuario por email") from exc

    def update(self, id: int, user_data: dict) -> User:
        """Actualizar usuario"""
        try:
            return self._update_user(id, user_data)
        except AppException:
            raise
        except Exception as exc:
            raise InternalServerError("Error actualizando usuario") from exc
