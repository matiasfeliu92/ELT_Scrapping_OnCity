from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.repositories.auth_repository import AuthRepository


class LoginUser:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def __call__(self, credentials: AuthCredentials) -> str:
        user = self.repo.find_by_email(credentials.email)

        if not user:
            raise ValueError("Credenciales invalidas")

        if not user.can_authenticate():
            raise ValueError("Usuario inactivo")

        if not self.repo.verify_password(credentials.password, user.password_hash):
            raise ValueError("Credenciales invalidas")

        token = self.repo.generate_access_token(user)
        self.repo.persist_token(user.id, token)
        return token
