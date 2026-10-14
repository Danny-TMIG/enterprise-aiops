"""Coherence: two representations of the same value agree."""

from __future__ import annotations

from typing import Any

from ..verify import canonical


def coherent(a: Any, b: Any) -> bool:
    return canonical(a) == canonical(b)


def incoherent_keys(a: dict, b: dict) -> list[str]:
    out: list[str] = []
    for k in sorted(set(a) | set(b)):
        if canonical(a.get(k)) != canonical(b.get(k)):
            out.append(k)
    return out


# ── coherent / incoherent_keys ──────────────────────────────────────
from dcs.verify import canonical as _canonical


def coherent(a, b):
    """True if a and b have the same canonical form."""
    return _canonical(a) == _canonical(b)


def incoherent_keys(a, b):
    """Keys whose canonical forms differ between a and b."""
    out = []
    for k in sorted(set(a) | set(b)):
        if _canonical(a.get(k)) != _canonical(b.get(k)):
            out.append(k)
    return out
