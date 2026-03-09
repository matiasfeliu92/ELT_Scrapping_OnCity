from dataclasses import dataclass

@dataclass(frozen=True)
class Name:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("Name must be a non-empty string")
        if len(self.value) > 100:
            raise ValueError("Name must be at most 100 characters")