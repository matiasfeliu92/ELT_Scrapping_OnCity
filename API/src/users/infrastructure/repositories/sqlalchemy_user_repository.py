from typing import List, Optional
from sqlalchemy.orm import Session
from API.src.users.domain.entities.user import User
from API.src.users.domain.repositories.user_repository import UserRepository
from API.src.users.infrastructure.models.user import User as UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def _map_model_to_entity(self, model: UserModel) -> User:
        """Mapear modelo SQLAlchemy a entidad de dominio"""
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            location=model.location,
            phone=model.phone,
            is_active=model.is_active,
            is_admin=model.is_admin,
            password=model.password
        )

    def find_all(self) -> List[User]:
        """Obtener todos los usuarios"""
        users = self.session.query(UserModel).filter(
            UserModel.is_active == True
        ).order_by(UserModel.id.asc()).all()
        
        return [self._map_model_to_entity(user) for user in users]

    def find_by_id(self, id: int) -> Optional[User]:
        """Buscar usuario por ID"""
        user_model = self.session.query(UserModel).filter(
            UserModel.id == id
        ).first()
        
        if not user_model:
            return None
        
        return self._map_model_to_entity(user_model)

    def find_by_email(self, email: str) -> Optional[User]:
        """Buscar usuario por email"""
        user_model = self.session.query(UserModel).filter(
            UserModel.email == email
        ).first()
        
        if not user_model:
            return None
        
        return self._map_model_to_entity(user_model)

    def update(self, id: int, user_data: dict) -> User:
        """Actualizar usuario"""
        user_model = self.session.query(UserModel).filter(
            UserModel.id == id
        ).first()
        
        if not user_model:
            raise ValueError(f"Usuario con ID {id} no encontrado")
        
        # Actualizar solo los campos permitidos
        allowed_fields = ['name', 'is_active']
        for key, value in user_data.items():
            if key in allowed_fields and hasattr(user_model, key):
                setattr(user_model, key, value)
        
        self.session.commit()
        self.session.refresh(user_model)
        
        return self._map_model_to_entity(user_model)