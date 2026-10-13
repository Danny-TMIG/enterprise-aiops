"""Constructive Self-Transcendence — the four operations.

A CSTLoop wraps the four operations required by the predicate:

    articulate : () -> Test
    justify    : Test -> LegitimacyProof
    acquire    : Test -> Capability
    undo       : Capability -> bool

The loop is considered complete only if all four return successfully.
If undo fails, the loop scores zero — the system has drifted.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Test:
    name: str
    payload: Any
    baseline_success: float   # in [0, 1]; the system's success before acquisition
    target_success: float     # in [0, 1]; the required success to pass


@dataclass
class LegitimacyProof:
    non_vacuous: bool
    non_arbitrary: bool
    grounded: bool
    invariant: str | None = None
    reason: str = ""

    @property
    def valid(self) -> bool:
        return self.non_vacuous and self.non_arbitrary and self.grounded


@dataclass
class Capability:
    test_name: str
    acquired: bool
    artifact: Any = None
    detail: str = ""


@dataclass
class CSTLoop:
    articulate: Callable[[], Test | None]
    justify: Callable[[Test], LegitimacyProof]
    acquire: Callable[[Test], Capability]
    undo: Callable[[Capability], bool]

    completed: list[dict[str, Any]] = field(default_factory=list)

    def run_once(self) -> dict[str, Any] | None:
        t = self.articulate()
        if t is None:
            return None

        proof = self.justify(t)
        if not proof.valid:
            return {"test": t.name, "status": "illegitimate",
                    "reason": proof.reason}

        cap = self.acquire(t)
        if not cap.acquired:
            return {"test": t.name, "status": "not-acquired"}

        # If we cannot undo, the loop does not count.
        if not self.undo(cap):
            return {"test": t.name, "status": "no-undo"}

        nt = _nontriviality(t)
        rec = {
            "test": t.name,
            "status": "complete",
            "nontriviality": round(nt, 4),
            "reversibility": 1.0,
            "invariant": proof.invariant,
        }
        self.completed.append(rec)
        return rec


def _nontriviality(t: Test) -> float:
    """How much room is there between current and target success?"""
    if t.target_success <= 0:
        return 0.0
    gap = t.target_success - t.baseline_success
    if gap <= 0:
        return 0.0  # already passed; not a test
    return min(1.0, gap / t.target_success)
