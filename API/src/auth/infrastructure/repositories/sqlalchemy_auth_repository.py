from datetime import datetime, timedelta, timezone
import hashlib
import os
import secrets

import bcrypt
import jwt
from sqlalchemy.orm import Session

from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.domain.entities.auth_user import AuthUser
from API.src.auth.domain.repositories.auth_repository import AuthRepository
from API.src.auth.infrastructure.models.auth_token import AuthToken as AuthTokenModel
from API.src.users.infrastructure.models.user import User as UserModel


class SQLAlchemyAuthRepository(AuthRepository):
    def __init__(self, session: Session, jwt_secret_key: str | None = None):
        self.session = session
        # Fallback to a secure ephemeral key if no env var is provided.
        self.jwt_secret_key = jwt_secret_key or os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(48)
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expiration_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    def _map_user_model_to_entity(self, model: UserModel) -> AuthUser:
        return AuthUser(
            id=model.id,
            email=model.email,
            password_hash=model.password,
            is_active=model.is_active,
            name=model.name,
        )

    def find_by_email(self, email: str) -> AuthUser | None:
        user_model = self.session.query(UserModel).filter(UserModel.email == email).first()
        if not user_model:
            return None
        return self._map_user_model_to_entity(user_model)

    def create_user(self, credentials: AuthCredentials) -> AuthUser:
        hashed_password = self.hash_password(credentials.password)

        user_model = UserModel(
            name=credentials.name,
            email=credentials.email,
            password=hashed_password,
            location=credentials.location,
            phone=credentials.phone,
            is_admin=False,
            is_active=True,
        )

        self.session.add(user_model)
        self.session.commit()
        self.session.refresh(user_model)

        return self._map_user_model_to_entity(user_model)

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))

    def generate_access_token(self, user: AuthUser) -> str:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(minutes=self.access_token_expiration_minutes)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "jti": user.generate_token_id(),
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
        }

        return jwt.encode(payload, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def verify_access_token(self, token: str) -> dict:
        payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
        token_hash = self._hash_token(token)

        db_token = self.session.query(AuthTokenModel).filter(
            AuthTokenModel.token_hash == token_hash,
            AuthTokenModel.is_revoked == False,
            AuthTokenModel.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
        ).first()

        if not db_token:
            raise ValueError("Token invalido o revocado")

        return payload

    def persist_token(self, user_id: int, token: str) -> None:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        exp = unverified_payload.get("exp")
        if not exp:
            raise ValueError("Token sin expiracion")

        token_row = AuthTokenModel(
            user_id=user_id,
            token_hash=self._hash_token(token),
            expires_at=datetime.fromtimestamp(exp),
            is_revoked=False,
        )

        self.session.add(token_row)
        self.session.commit()

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
