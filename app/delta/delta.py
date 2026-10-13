"""Compute the delta between two probes. Classify into quadrants."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.delta.probe import Probe


class Quadrant(str, Enum):
    BOTH_PASS = "both_pass"
    BOTH_FAIL = "both_fail"
    A_BEATS_B = "A_beats_B"
    B_BEATS_A = "B_beats_A"


@dataclass
class Delta:
    workload_id: str
    input_value: Any
    prompt: str
    a: Probe
    b: Probe
    quadrant: Quadrant

    @property
    def teacher(self) -> Probe | None:
        if self.quadrant == Quadrant.A_BEATS_B: return self.a
        if self.quadrant == Quadrant.B_BEATS_A: return self.b
        return None

    @property
    def student(self) -> Probe | None:
        if self.quadrant == Quadrant.A_BEATS_B: return self.b
        if self.quadrant == Quadrant.B_BEATS_A: return self.a
        return None

    @property
    def is_signal(self) -> bool:
        return self.quadrant in (Quadrant.A_BEATS_B, Quadrant.B_BEATS_A)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "quadrant": self.quadrant.value,
            "a": self.a.to_dict(),
            "b": self.b.to_dict(),
        }


def classify(a: Probe, b: Probe, workload_id: str,
             input_value: Any, prompt: str) -> Delta:
    if a.passed and b.passed:
        q = Quadrant.BOTH_PASS
    elif not a.passed and not b.passed:
        q = Quadrant.BOTH_FAIL
    elif a.passed and not b.passed:
        q = Quadrant.A_BEATS_B
    else:
        q = Quadrant.B_BEATS_A
    return Delta(workload_id=workload_id, input_value=input_value,
                 prompt=prompt, a=a, b=b, quadrant=q)


def delta_set(probes_a: list[Probe], probes_b: list[Probe]) -> list[Delta]:
    by_a = {(p.workload_id, repr(p.input_value)): p for p in probes_a}
    by_b = {(p.workload_id, repr(p.input_value)): p for p in probes_b}
    out: list[Delta] = []
    for key, pa in by_a.items():
        pb = by_b.get(key)
        if pb is None:
            continue
        out.append(classify(pa, pb, key[0], pa.input_value, pa.prompt))
    return out


def summarize(deltas: list[Delta]) -> dict[str, int]:
    from collections import Counter
    c = Counter(d.quadrant.value for d in deltas)
    return {
        "total": len(deltas),
        "both_pass": c["both_pass"],
        "both_fail": c["both_fail"],
        "A_beats_B": c["A_beats_B"],
        "B_beats_A": c["B_beats_A"],
        "signal": c["A_beats_B"] + c["B_beats_A"],
    }
