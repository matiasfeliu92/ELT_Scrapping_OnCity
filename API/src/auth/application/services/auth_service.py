from API.src.auth.application.use_cases.login_user import LoginUser
from API.src.auth.application.use_cases.register_user import RegisterUser
from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo
        self._register_user = RegisterUser(repo)
        self._login_user = LoginUser(repo)

    def register(self, credentials: AuthCredentials) -> str:
        return self._register_user(credentials)

    def login(self, credentials: AuthCredentials) -> str:
        return self._login_user(credentials)
