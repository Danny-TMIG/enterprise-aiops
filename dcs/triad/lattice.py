"""Belnap FOUR — the algebraic substrate of the triad kernel.

    UNKNOWN  = (0, 0)  neither proven
    PASS     = (1, 0)  proven true
    FAIL     = (0, 1)  proven false
    CONFLICT = (1, 1)  both proven

Two monotone orders:
    truth:      FAIL < UNKNOWN,CONFLICT < PASS
    knowledge:  UNKNOWN < PASS,FAIL < CONFLICT
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class VState:
    t: int
    f: int

    def __post_init__(self):
        if self.t not in (0, 1) or self.f not in (0, 1):
            raise ValueError(f"coordinates must be 0/1, got ({self.t},{self.f})")

    @property
    def name(self) -> str:
        return {(0, 0): "UNKNOWN", (1, 0): "PASS", (0, 1): "FAIL", (1, 1): "CONFLICT"}[
            (self.t, self.f)
        ]

    def __repr__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {"t": self.t, "f": self.f, "name": self.name}

    @classmethod
    def from_any(cls, x) -> VState:
        if isinstance(x, cls):
            return x
        if isinstance(x, dict):
            return cls(int(x.get("t", 0)), int(x.get("f", 0)))
        if isinstance(x, str):
            return {"UNKNOWN": UNKNOWN, "PASS": PASS, "FAIL": FAIL, "CONFLICT": CONFLICT}[x.upper()]
        raise TypeError(f"cannot coerce {x!r} to VState")


UNKNOWN = VState(0, 0)
PASS = VState(1, 0)
FAIL = VState(0, 1)
CONFLICT = VState(1, 1)
ALL_STATES = (UNKNOWN, PASS, FAIL, CONFLICT)


# ---------- orders ----------


def truth_le(a, b) -> bool:
    """a ⊑_t b  iff  a.t ≤ b.t  and  a.f ≥ b.f."""
    return a.t <= b.t and a.f >= b.f


def know_le(a, b) -> bool:
    """a ⊑_k b  iff  a.t ≤ b.t  and  a.f ≤ b.f."""
    return a.t <= b.t and a.f <= b.f


# ---------- lattice operations ----------


def meet_truth(a, b):
    """Conjunction (both must hold)."""
    return VState(min(a.t, b.t), max(a.f, b.f))


def join_truth(a, b):
    """Disjunction (either may hold)."""
    return VState(max(a.t, b.t), min(a.f, b.f))


def meet_know(a, b):
    """Common information."""
    return VState(min(a.t, b.t), min(a.f, b.f))


def join_know(a, b):
    """Union of information."""
    return VState(max(a.t, b.t), max(a.f, b.f))


# ---------- folds ----------


def fold_v(states: Iterable[VState], op, *, empty=None) -> VState:
    it = iter(states)
    try:
        acc = next(it)
    except StopIteration:
        return empty if empty is not None else UNKNOWN
    for s in it:
        acc = op(acc, s)
    return acc


def consensus(states) -> VState:
    """Unanimous agreement, otherwise CONFLICT."""
    s = [VState.from_any(x) for x in states]
    if not s:
        return UNKNOWN
    return s[0] if all(x == s[0] for x in s) else CONFLICT


def quorum(states) -> VState:
    """Strict-majority PASS → PASS; strict-majority FAIL → FAIL; else CONFLICT."""
    s = [VState.from_any(x) for x in states]
    if not s:
        return UNKNOWN
    n = len(s)
    p = sum(1 for x in s if x == PASS)
    f = sum(1 for x in s if x == FAIL)
    if p > n // 2:
        return PASS
    if f > n // 2:
        return FAIL
    return CONFLICT
