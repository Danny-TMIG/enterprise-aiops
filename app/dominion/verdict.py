"""Verdict taxonomy for the chain roles and witness.

Four states, no fifth. Every role returns one. Nothing invented
beyond what chain/witness.py and chain/roles.py import.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Verdict:
    state: str                  # "pass" | "fail" | "unknown" | "error"
    detail: str = ""
    witness_id: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def ok(self) -> bool:
        return self.state == "pass"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# the four canonical verdicts, as module-level constants so
# chain/witness.py can `from app.dominion.verdict import PASS, FAIL`
PASS    = Verdict(state="pass")
FAIL    = Verdict(state="fail")
UNKNOWN = Verdict(state="unknown")
ERROR   = Verdict(state="error")


__all__ = ["Verdict", "PASS", "FAIL", "UNKNOWN", "ERROR"]
