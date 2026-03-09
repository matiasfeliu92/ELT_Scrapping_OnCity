from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.repositories.auth_repository import AuthRepository
from API.src.shared.exceptions import AuthenticationError
from API.src.shared.exceptions.base import NotFoundError


class LoginUser:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def __call__(self, credentials: AuthCredentials) -> str:
        user = self.repo.find_by_email(credentials.email)

        if not user:
            raise NotFoundError("El usuario no existe")

        if not user.can_authenticate():
            raise AuthenticationError("Usuario inactivo")

        if not self.repo.verify_password(credentials.password, user.password_hash):
            raise AuthenticationError("Credenciales invalidas")

        token = self.repo.generate_access_token(user)
        self.repo.persist_token(user.id, token)
        return token
