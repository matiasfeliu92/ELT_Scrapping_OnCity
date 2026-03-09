from dataclasses import dataclass

@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not self.value:
            raise ValueError("Password must be a non-empty string")
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")