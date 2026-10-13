"""Coherence: do two artifacts agree with each other?"""

from __future__ import annotations  # pragma: no cover

from collections.abc import Callable, Iterable  # pragma: no cover
from typing import Any  # pragma: no cover

from dcs.triad.lattice import (  # pragma: no cover
    FAIL,
    PASS,
    UNKNOWN,
    VState,
    fold_v,
    join_know,
)


def equivalence(a: Any, b: Any, *, eq: Callable[[Any, Any], bool]) -> VState:  # pragma: no cover
    try:
        return PASS if eq(a, b) else FAIL  # pragma: no cover
    except Exception:  # pragma: no cover
        return UNKNOWN  # pragma: no cover


def refinement(a: Any, b: Any, *, implies: Callable[[Any, Any], bool]) -> VState:  # pragma: no cover
    try:
        return PASS if implies(a, b) else FAIL  # pragma: no cover
    except Exception:  # pragma: no cover
        return UNKNOWN  # pragma: no cover


def incompatible(a: Any, b: Any, *, disjoint: Callable[[Any, Any], bool]) -> VState:  # pragma: no cover
    try:
        return PASS if disjoint(a, b) else FAIL  # pragma: no cover
    except Exception:  # pragma: no cover
        return UNKNOWN  # pragma: no cover


def relation(a: Any, b: Any, *, rel: Callable[[Any, Any], bool | None]) -> VState:  # pragma: no cover
    try:
        got = rel(a, b)
    except Exception:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    if got is None:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    return PASS if got else FAIL  # pragma: no cover


def combine(states: Iterable[VState]) -> VState:  # pragma: no cover
    """Union of information across coherent views."""
    return fold_v((VState.from_any(x) for x in states), join_know)  # pragma: no cover
