"""Belnap sources — the kernel of dcs.

A source attests to a requirement's state. The engine folds all sources
into a single Belnap FOUR verdict. Binary sources collapse; Belnap
sources surface disagreement as CONFLICT.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class B(str, Enum):
    """Belnap FOUR: T (true), F (false), U (unknown), B (both/conflict).

    Subclasses str so dataclass asdict() + json.dumps() work without a
    custom encoder.
    """
    T = "T"
    F = "F"
    U = "U"
    B = "B"


@dataclass(frozen=True)
class Attestation:
    req_id: str
    state: B
    source: str
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


_SOURCES: dict[str, list[Callable[[], Attestation]]] = {}


def source(req_id: str):
    """Register a source function for a requirement id."""
    def deco(fn):
        _SOURCES.setdefault(req_id, []).append(fn)
        return fn
    return deco


def sources_for(req_id: str) -> list[Callable[[], Attestation]]:
    return list(_SOURCES.get(req_id, []))


def meet(a: B, b: B) -> B:
    """Belnap meet (AND): T∧T=T, T∧F=B, U identity, B absorbing."""
    if a == b: return a
    if a == B.U: return b
    if b == B.U: return a
    if a == B.B or b == B.B: return B.B
    return B.B  # T and F


def join(a: B, b: B) -> B:
    """Belnap join (OR): F∨F=F, T∨F=B, U identity, B absorbing."""
    if a == b: return a
    if a == B.U: return b
    if b == B.U: return a
    if a == B.B or b == B.B: return B.B
    return B.B


def fold(atts: list[Attestation]) -> B:
    """Fold attestations via meet. Empty → U."""
    if not atts:
        return B.U
    s = atts[0].state
    for a in atts[1:]:
        s = meet(s, a.state)
    return s
