from dataclasses import dataclass
from typing import Optional
import secrets


@dataclass
class AuthUser:
    id: int
    email: str
    password_hash: str
    is_active: bool
    name: Optional[str] = None

    def can_authenticate(self) -> bool:
        return self.is_active

    @staticmethod
    def generate_token_id() -> str:
        # 256-bit token identifier used as JWT jti.
        return secrets.token_urlsafe(32)
