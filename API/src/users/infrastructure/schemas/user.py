from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    password: str
    location: Optional[str]
    phone: Optional[str]
    is_admin: bool
    is_active: bool

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    location: Optional[str]
    phone: Optional[str]
    is_admin: bool
    is_active: bool

class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None