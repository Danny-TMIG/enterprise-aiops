"""Verdict taxonomy for the chain roles and witness.

Four states, no fifth. Every role returns one. Nothing invented
beyond what chain/witness.py and chain/roles.py import.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Verdict:
    state: str                  # "pass" | "fail" | "unknown" | "error"
    detail: str = ""
    witness_id: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def ok(self) -> bool:
        return self.state == "pass"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# the four canonical verdicts, as module-level constants so
# chain/witness.py can `from app.dominion.verdict import PASS, FAIL`
PASS    = Verdict(state="pass")
FAIL    = Verdict(state="fail")
UNKNOWN = Verdict(state="unknown")
ERROR   = Verdict(state="error")


__all__ = ["ERROR", "FAIL", "PASS", "UNKNOWN", "Verdict"]
