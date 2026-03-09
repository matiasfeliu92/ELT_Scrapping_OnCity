from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.repositories.auth_repository import AuthRepository
from API.src.shared.exceptions import ValidationError
from API.src.shared.exceptions.base import AlreadyExistsError


class RegisterUser:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def __call__(self, credentials: AuthCredentials) -> str:
        credentials.validate_password_strength()

        if not credentials.name:
            raise ValidationError("El nombre es requerido para registrar un usuario")

        existing_user = self.repo.find_by_email(credentials.email)
        if existing_user:
            raise AlreadyExistsError("El email ya esta registrado")

        user = self.repo.create_user(credentials)
        token = self.repo.generate_access_token(user)
        self.repo.persist_token(user.id, token)
        return token
