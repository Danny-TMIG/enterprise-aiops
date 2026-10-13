"""Two human gates. One review. One decision. Not per-agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class GateError(RuntimeError):
    pass


@dataclass
class GateDecision:
    gate: str
    approved: bool
    by: str
    note: str = ""
    ts: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {"gate": self.gate, "approved": self.approved,
                "by": self.by, "note": self.note, "ts": self.ts}


@dataclass
class Gate:
    name: str
    decision: GateDecision | None = None

    @property
    def passed(self) -> bool:
        return bool(self.decision and self.decision.approved)

    def approve(self, by: str, note: str = "") -> GateDecision:
        if self.decision is not None:
            raise GateError(f"gate '{self.name}' already decided")
        self.decision = GateDecision(self.name, True, by, note)
        return self.decision

    def reject(self, by: str, note: str = "") -> GateDecision:
        if self.decision is not None:
            raise GateError(f"gate '{self.name}' already decided")
        self.decision = GateDecision(self.name, False, by, note)
        return self.decision

    def require(self) -> None:
        if not self.passed:
            raise GateError(f"gate '{self.name}' not passed")

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name,
                "decision": self.decision.to_dict() if self.decision else None,
                "passed": self.passed}
