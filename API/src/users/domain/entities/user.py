from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    password: str
    location: Optional[str]
    phone: Optional[str]
    is_admin: bool
    is_active: bool