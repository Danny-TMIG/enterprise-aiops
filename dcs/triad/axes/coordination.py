"""Coordination: do many agents agree together?"""

from __future__ import annotations  # pragma: no cover

from collections.abc import Iterable  # pragma: no cover

from dcs.triad.lattice import (  # pragma: no cover
    CONFLICT,
    FAIL,
    PASS,
    UNKNOWN,
    VState,
    fold_v,
    join_know,
    join_truth,
    meet_truth,
)
from dcs.triad.lattice import (  # pragma: no cover
    consensus as _consensus,
)
from dcs.triad.lattice import (  # pragma: no cover
    quorum as _quorum,
)


def _coerce(x) -> VState:  # pragma: no cover
    return VState.from_any(x)  # pragma: no cover


def merge(states: Iterable[VState]) -> VState:  # pragma: no cover
    return fold_v((_coerce(x) for x in states), join_know)  # pragma: no cover


def conjunction(states: Iterable[VState]) -> VState:  # pragma: no cover
    return fold_v((_coerce(x) for x in states), meet_truth)  # pragma: no cover


def disjunction(states: Iterable[VState]) -> VState:  # pragma: no cover
    return fold_v((_coerce(x) for x in states), join_truth)  # pragma: no cover


def consensus(states: Iterable[VState]) -> VState:  # pragma: no cover
    return _consensus(states)  # pragma: no cover


def quorum(states: Iterable[VState]) -> VState:  # pragma: no cover
    return _quorum(states)  # pragma: no cover


def veto(states: Iterable[VState]) -> VState:  # pragma: no cover
    """Any FAIL vetoes; any CONFLICT poisons."""
    s = [_coerce(x) for x in states]
    if not s:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    if any(x == CONFLICT for x in s):  # pragma: no cover
        return CONFLICT  # pragma: no cover
    if any(x == FAIL for x in s):  # pragma: no cover
        return FAIL  # pragma: no cover
    if all(x == PASS for x in s):  # pragma: no cover
        return PASS  # pragma: no cover
    return UNKNOWN  # pragma: no cover


def weighted(states: Iterable[VState], *, weights: Iterable[float] | None = None) -> VState:  # pragma: no cover
    s = [_coerce(x) for x in states]
    if not s:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    w = list(weights) if weights is not None else [1.0] * len(s)
    if len(w) != len(s):  # pragma: no cover
        raise ValueError("weights length mismatch")  # pragma: no cover
    total = sum(w)
    if total <= 0:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    p = sum(wi for wi, st in zip(w, s, strict=True) if st == PASS)
    f = sum(wi for wi, st in zip(w, s, strict=True) if st == FAIL)
    if p == 0 and f == 0:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    if p > f:  # pragma: no cover
        return PASS  # pragma: no cover
    if f > p:  # pragma: no cover
        return FAIL  # pragma: no cover
    return CONFLICT  # pragma: no cover
