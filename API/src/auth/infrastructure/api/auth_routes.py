from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from API.src.auth.application.services.auth_service import AuthService
from API.src.auth.domain.entities.auth_credentials import AuthCredentials
from API.src.auth.infrastructure.repositories.sqlalchemy_auth_repository import SQLAlchemyAuthRepository
from API.src.auth.infrastructure.schemas.auth import (
    AuthTokenResponse,
    LoginUserRequest,
    RegisterUserRequest,
)
from API.src.shared.infrastructure.db.config import Config


auth_router = APIRouter(prefix="/v1/auth")
config = Config()
get_db = config.get_db


@auth_router.post("/register", response_model=AuthTokenResponse)
def register_user(payload: RegisterUserRequest, db: Session = Depends(get_db)):
    repo = SQLAlchemyAuthRepository(db)
    service = AuthService(repo)

    credentials = AuthCredentials(
        email=payload.email,
        password=payload.password,
        name=payload.name,
        location=payload.location,
        phone=payload.phone,
    )

    token = service.register(credentials)
    return AuthTokenResponse(access_token=token)


@auth_router.post("/login", response_model=AuthTokenResponse)
def login_user(payload: LoginUserRequest, db: Session = Depends(get_db)):
    repo = SQLAlchemyAuthRepository(db)
    service = AuthService(repo)

    credentials = AuthCredentials(email=payload.email, password=payload.password)

    token = service.login(credentials)
    return AuthTokenResponse(access_token=token)
