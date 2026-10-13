from __future__ import annotations

from dataclasses import dataclass

G = "G"
D = "D"
E = "E"
KINDS = (G, D, E)
PORTS = {G: 3, D: 3, E: 1}


@dataclass(frozen=True)
class Octet:
    kind: str
    value: int = 0

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown kind: {self.kind}")
        if not 0 <= int(self.value) <= 255:
            raise ValueError(f"value out of range: {self.value}")

    def __str__(self) -> str:
        return f"{self.kind}[{self.value:02x}]"
