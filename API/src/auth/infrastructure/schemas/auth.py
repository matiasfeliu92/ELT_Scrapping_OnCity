from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str
    location: Optional[str] = None
    phone: Optional[str] = None


class LoginUserRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
