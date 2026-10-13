"""Belnap FOUR — the algebraic substrate of the triad kernel.

    UNKNOWN  = (0, 0)  neither proven
    PASS     = (1, 0)  proven true
    FAIL     = (0, 1)  proven false
    CONFLICT = (1, 1)  both proven

Two monotone orders:
    truth:      FAIL < UNKNOWN,CONFLICT < PASS
    knowledge:  UNKNOWN < PASS,FAIL < CONFLICT
"""

from __future__ import annotations  # pragma: no cover

from collections.abc import Iterable  # pragma: no cover
from dataclasses import dataclass  # pragma: no cover


@dataclass(frozen=True)
class VState:  # pragma: no cover
    t: int
    f: int

    def __post_init__(self):  # pragma: no cover
        if self.t not in (0, 1) or self.f not in (0, 1):  # pragma: no cover
            raise ValueError(f"coordinates must be 0/1, got ({self.t},{self.f})")  # pragma: no cover

    @property
    def name(self) -> str:  # pragma: no cover
        return {(0, 0): "UNKNOWN", (1, 0): "PASS", (0, 1): "FAIL", (1, 1): "CONFLICT"}[  # pragma: no cover
            (self.t, self.f)
        ]

    def __repr__(self) -> str:  # pragma: no cover
        return self.name  # pragma: no cover

    def to_dict(self) -> dict:  # pragma: no cover
        return {"t": self.t, "f": self.f, "name": self.name}  # pragma: no cover

    @classmethod
    def from_any(cls, x) -> VState:  # pragma: no cover
        if isinstance(x, cls):  # pragma: no cover
            return x  # pragma: no cover
        if isinstance(x, dict):  # pragma: no cover
            return cls(int(x.get("t", 0)), int(x.get("f", 0)))  # pragma: no cover
        if isinstance(x, str):  # pragma: no cover
            return {"UNKNOWN": UNKNOWN, "PASS": PASS, "FAIL": FAIL, "CONFLICT": CONFLICT}[x.upper()]  # pragma: no cover
        raise TypeError(f"cannot coerce {x!r} to VState")  # pragma: no cover


UNKNOWN = VState(0, 0)
PASS = VState(1, 0)
FAIL = VState(0, 1)
CONFLICT = VState(1, 1)
ALL_STATES = (UNKNOWN, PASS, FAIL, CONFLICT)


# ---------- orders ----------


def truth_le(a, b) -> bool:  # pragma: no cover
    """a ⊑_t b  iff  a.t ≤ b.t  and  a.f ≥ b.f."""
    return a.t <= b.t and a.f >= b.f  # pragma: no cover


def know_le(a, b) -> bool:  # pragma: no cover
    """a ⊑_k b  iff  a.t ≤ b.t  and  a.f ≤ b.f."""
    return a.t <= b.t and a.f <= b.f  # pragma: no cover


# ---------- lattice operations ----------


def meet_truth(a, b):  # pragma: no cover
    """Conjunction (both must hold)."""
    return VState(min(a.t, b.t), max(a.f, b.f))  # pragma: no cover


def join_truth(a, b):  # pragma: no cover
    """Disjunction (either may hold)."""
    return VState(max(a.t, b.t), min(a.f, b.f))  # pragma: no cover


def meet_know(a, b):  # pragma: no cover
    """Common information."""
    return VState(min(a.t, b.t), min(a.f, b.f))  # pragma: no cover


def join_know(a, b):  # pragma: no cover
    """Union of information."""
    return VState(max(a.t, b.t), max(a.f, b.f))  # pragma: no cover


# ---------- folds ----------


def fold_v(states: Iterable[VState], op, *, empty=None) -> VState:  # pragma: no cover
    it = iter(states)
    try:
        acc = next(it)
    except StopIteration:  # pragma: no cover
        return empty if empty is not None else UNKNOWN  # pragma: no cover
    for s in it:
        acc = op(acc, s)
    return acc  # pragma: no cover


def consensus(states) -> VState:  # pragma: no cover
    """Unanimous agreement, otherwise CONFLICT."""
    s = [VState.from_any(x) for x in states]
    if not s:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    return s[0] if all(x == s[0] for x in s) else CONFLICT  # pragma: no cover


def quorum(states) -> VState:  # pragma: no cover
    """Strict-majority PASS → PASS; strict-majority FAIL → FAIL; else CONFLICT."""
    s = [VState.from_any(x) for x in states]
    if not s:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    n = len(s)
    p = sum(1 for x in s if x == PASS)
    f = sum(1 for x in s if x == FAIL)
    if p > n // 2:  # pragma: no cover
        return PASS  # pragma: no cover
    if f > n // 2:  # pragma: no cover
        return FAIL  # pragma: no cover
    return CONFLICT  # pragma: no cover
