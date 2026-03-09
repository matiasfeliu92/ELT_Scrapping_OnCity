from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Id:
    value: Optional[int]

    def __post_init__(self):
        if self.value is None:
            return
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("Id must be a positive integer or None")