from API.src.auth.application.use_cases.login_user import LoginUser
from API.src.auth.application.use_cases.register_user import RegisterUser
from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.repositories.auth_repository import AuthRepository
from API.src.shared.exceptions import AppException, InternalServerError


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo
        self._register_user = RegisterUser(repo)
        self._login_user = LoginUser(repo)

    def register(self, credentials: AuthCredentials) -> str:
        try:
            return self._register_user(credentials)
        except AppException:
            raise
        except Exception as exc:
            raise InternalServerError("Error registrando usuario") from exc

    def login(self, credentials: AuthCredentials) -> str:
        try:
            return self._login_user(credentials)
        except AppException:
            raise
        except Exception as exc:
            raise InternalServerError("Error autenticando usuario") from exc
