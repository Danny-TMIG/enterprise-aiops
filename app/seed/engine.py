import hashlib
import time
from typing import Any


class SeedEngine:
    def __init__(self, seed_value: int = 42):
        self.seed_value = seed_value
        self.created_at = time.time()

    def generate_state(self) -> dict[str, Any]:
        h = hashlib.sha256(str(self.seed_value).encode()).hexdigest()
        return {
            "seed": self.seed_value,
            "hash": h,
            "status": "seeded",
            "timestamp": self.created_at
        }

    def verify(self, state_hash: str) -> bool:
        expected = hashlib.sha256(str(self.seed_value).encode()).hexdigest()
        return expected == state_hash
