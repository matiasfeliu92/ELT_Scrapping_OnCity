from dataclasses import dataclass
import re

_EMAIL_RE = re.compile(r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+$")

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("Email must be a non-empty string")
        if not _EMAIL_RE.fullmatch(self.value.strip()):
            raise ValueError("Invalid email address")