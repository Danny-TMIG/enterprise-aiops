"""Coordination: do many agents agree together?"""
from __future__ import annotations
from typing import Iterable, List
from dcs.triad.lattice import (
    VState, PASS, FAIL, UNKNOWN, CONFLICT,
    fold_v, join_know, join_truth, meet_truth,
    consensus as _consensus, quorum as _quorum,
)


def _coerce(x) -> VState:
    return VState.from_any(x)


def merge(states: Iterable[VState]) -> VState:
    return fold_v((_coerce(x) for x in states), join_know)


def conjunction(states: Iterable[VState]) -> VState:
    return fold_v((_coerce(x) for x in states), meet_truth)


def disjunction(states: Iterable[VState]) -> VState:
    return fold_v((_coerce(x) for x in states), join_truth)


def consensus(states: Iterable[VState]) -> VState:
    return _consensus(states)


def quorum(states: Iterable[VState]) -> VState:
    return _quorum(states)


def veto(states: Iterable[VState]) -> VState:
    """Any FAIL vetoes; any CONFLICT poisons."""
    s = [_coerce(x) for x in states]
    if not s:
        return UNKNOWN
    if any(x == CONFLICT for x in s):
        return CONFLICT
    if any(x == FAIL for x in s):
        return FAIL
    if all(x == PASS for x in s):
        return PASS
    return UNKNOWN


def weighted(states: Iterable[VState], *,
             weights: Iterable[float] | None = None) -> VState:
    s = [_coerce(x) for x in states]
    if not s:
        return UNKNOWN
    w = list(weights) if weights is not None else [1.0] * len(s)
    if len(w) != len(s):
        raise ValueError("weights length mismatch")
    total = sum(w)
    if total <= 0:
        return UNKNOWN
    p = sum(wi for wi, st in zip(w, s) if st == PASS)
    f = sum(wi for wi, st in zip(w, s) if st == FAIL)
    if p == 0 and f == 0:
        return UNKNOWN
    if p > f:
        return PASS
    if f > p:
        return FAIL
    return CONFLICT
