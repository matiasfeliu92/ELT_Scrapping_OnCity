from dataclasses import dataclass
import re


_PASSWORD_POLICY_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)


@dataclass
class AuthCredentials:
    email: str
    password: str
    name: str | None = None
    location: str | None = None
    phone: str | None = None

    def __post_init__(self) -> None:
        self.email = self.email.strip().lower()
        if "@" not in self.email:
            raise ValueError("Email invalido")

    def validate_password_strength(self) -> None:
        if not _PASSWORD_POLICY_REGEX.match(self.password):
            raise ValueError(
                "La contrasena debe tener al menos 8 caracteres, una mayuscula, "
                "una minuscula, un numero y un simbolo"
            )
