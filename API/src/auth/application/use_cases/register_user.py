from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.repositories.auth_repository import AuthRepository


class RegisterUser:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def __call__(self, credentials: AuthCredentials) -> str:
        credentials.validate_password_strength()

        if not credentials.name:
            raise ValueError("El nombre es requerido para registrar un usuario")

        existing_user = self.repo.find_by_email(credentials.email)
        if existing_user:
            raise ValueError("El email ya esta registrado")

        user = self.repo.create_user(credentials)
        token = self.repo.generate_access_token(user)
        self.repo.persist_token(user.id, token)
        return token
