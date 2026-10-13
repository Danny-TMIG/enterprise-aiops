from dataclasses import dataclass, field
from typing import Any

from app.core.manifest import CPVO


class CPVOMeter:
    def __init__(self, cpvo):
        self.cpvo = cpvo

@dataclass
class Workflow:
    intent: str
    manifest: Any
    cpvo: CPVOMeter = field(init=False)

    def __post_init__(self) -> None:
        cpv_data = getattr(self.manifest, "cpvo", CPVO())
        self.cpvo = CPVOMeter(cpv_data)

def from_cli(text: str, target: str = None, author: str = None) -> str:
    return text
