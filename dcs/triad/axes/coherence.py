"""Coherence: do two artifacts agree with each other?"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from dcs.triad.lattice import FAIL, PASS, UNKNOWN, VState, fold_v, join_know


def equivalence(a: Any, b: Any, *, eq: Callable[[Any, Any], bool]) -> VState:
    try:
        return PASS if eq(a, b) else FAIL
    except Exception:
        return UNKNOWN


def refinement(a: Any, b: Any, *, implies: Callable[[Any, Any], bool]) -> VState:
    try:
        return PASS if implies(a, b) else FAIL
    except Exception:
        return UNKNOWN


def incompatible(a: Any, b: Any, *, disjoint: Callable[[Any, Any], bool]) -> VState:
    try:
        return PASS if disjoint(a, b) else FAIL
    except Exception:
        return UNKNOWN


def relation(a: Any, b: Any, *, rel: Callable[[Any, Any], bool | None]) -> VState:
    try:
        got = rel(a, b)
    except Exception:
        return UNKNOWN
    if got is None:
        return UNKNOWN
    return PASS if got else FAIL


def combine(states: Iterable[VState]) -> VState:
    """Union of information across coherent views."""
    return fold_v((VState.from_any(x) for x in states), join_know)
