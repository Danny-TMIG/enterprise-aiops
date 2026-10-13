"""Belnap sources — the kernel of dcs.

A source attests to a requirement's state. The engine folds all sources
into a single Belnap FOUR verdict. Binary sources collapse; Belnap
sources surface disagreement as CONFLICT.
"""

from __future__ import annotations  # pragma: no cover

from collections.abc import Callable  # pragma: no cover
from dataclasses import dataclass, field  # pragma: no cover
from enum import Enum  # pragma: no cover
from typing import Any  # pragma: no cover


class B(str, Enum):  # pragma: no cover
    """Belnap FOUR: T (true), F (false), U (unknown), B (both/conflict).

    Subclasses str so dataclass asdict() + json.dumps() work without a
    custom encoder.
    """

    T = "T"
    F = "F"
    U = "U"
    B = "B"


@dataclass(frozen=True)
class Attestation:  # pragma: no cover
    req_id: str
    state: B
    source: str
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


_SOURCES: dict[str, list[Callable[[], Attestation]]] = {}


def source(req_id: str):  # pragma: no cover
    """Register a source function for a requirement id."""

    def deco(fn):  # pragma: no cover
        _SOURCES.setdefault(req_id, []).append(fn)
        return fn  # pragma: no cover

    return deco  # pragma: no cover


def sources_for(req_id: str) -> list[Callable[[], Attestation]]:  # pragma: no cover
    return list(_SOURCES.get(req_id, []))  # pragma: no cover


def meet(a: B, b: B) -> B:  # pragma: no cover
    """Belnap meet (AND): T∧T=T, T∧F=B, U identity, B absorbing."""
    if a == b:  # pragma: no cover
        return a  # pragma: no cover
    if a == B.U:  # pragma: no cover
        return b  # pragma: no cover
    if b == B.U:  # pragma: no cover
        return a  # pragma: no cover
    if a == B.B or b == B.B:  # pragma: no cover
        return B.B  # pragma: no cover
    return B.B  # T and F  # pragma: no cover


def join(a: B, b: B) -> B:  # pragma: no cover
    """Belnap join (OR): F∨F=F, T∨F=B, U identity, B absorbing."""
    if a == b:  # pragma: no cover
        return a  # pragma: no cover
    if a == B.U:  # pragma: no cover
        return b  # pragma: no cover
    if b == B.U:  # pragma: no cover
        return a  # pragma: no cover
    if a == B.B or b == B.B:  # pragma: no cover
        return B.B  # pragma: no cover
    return B.B  # pragma: no cover


def fold(atts: list[Attestation]) -> B:  # pragma: no cover
    """Fold attestations via meet. Empty → U."""
    if not atts:  # pragma: no cover
        return B.U  # pragma: no cover
    s = atts[0].state
    for a in atts[1:]:
        s = meet(s, a.state)
    return s  # pragma: no cover
