from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from API.src.shared.infrastructure.db.config import Config
from API.src.users.application.services.user_service import UserService
from API.src.users.exceptions.user_not_found_error import UserNotFoundError
from API.src.users.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from API.src.users.infrastructure.schemas.user import UserResponse

user_router = APIRouter(prefix="/v1/users")
config = Config()
get_db = config.get_db

@user_router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    users = service.get_all()
    return [UserResponse.model_validate(u) for u in users]

@user_router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        user = service.get_by_id(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")