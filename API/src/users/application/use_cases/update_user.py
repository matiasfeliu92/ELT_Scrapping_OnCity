from API.src.users.domain.entities.user import User
from API.src.users.domain.repositories.user_repository import UserRepository
from API.src.shared.exceptions import NotFoundError, ValidationError


class UpdateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self, id: int, user_data: dict) -> User:
        # Verificar que el usuario existe
        user = self.repo.find_by_id(id)
        if not user:
            raise NotFoundError(f"Usuario con ID {id} no encontrado")

        # No permitir actualizar campos sensibles
        forbidden_fields = ['password', 'email', 'id']
        for field in forbidden_fields:
            if field in user_data:
                raise ValidationError(f"No se puede actualizar el campo '{field}'")

        # Actualizar usuario
        return self.repo.update(id, user_data)