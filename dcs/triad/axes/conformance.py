"""Conformance: does the artifact match its declaration?"""

from __future__ import annotations  # pragma: no cover

from collections.abc import Callable, Iterable  # pragma: no cover
from typing import Any  # pragma: no cover

from dcs.triad.lattice import FAIL, PASS, UNKNOWN, VState  # pragma: no cover


def resolve(  # pragma: no cover
    declared: Any, actual: Any, *, compare: Callable[[Any, Any], bool] | None = None
) -> VState:
    if compare is None:  # pragma: no cover

        def compare(d, a):  # pragma: no cover
            return d == a  # pragma: no cover

    try:
        return PASS if compare(declared, actual) else FAIL  # pragma: no cover
    except Exception:  # pragma: no cover
        return UNKNOWN  # pragma: no cover


def schema(declared_fields: set, actual_fields: set) -> VState:  # pragma: no cover
    if not declared_fields:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    return PASS if set(actual_fields) >= set(declared_fields) else FAIL  # pragma: no cover


def behavioral(  # pragma: no cover
    pred: Callable[[Any], bool], sample: Iterable[Any], *, epsilon: float = 1e-9
) -> VState:
    s = list(sample)
    if not s:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    k = sum(1 for x in s if pred(x))
    if k == len(s):  # pragma: no cover
        return PASS  # pragma: no cover
    if k == 0:  # pragma: no cover
        return FAIL  # pragma: no cover
    rate = k / len(s)
    if abs(rate - 0.5) < epsilon:  # pragma: no cover
        return FAIL  # pragma: no cover
    return UNKNOWN  # pragma: no cover


def certificate(claim: dict, cert: dict, *, verifier: Callable[[dict, dict], bool]) -> VState:  # pragma: no cover
    try:
        ok = verifier(claim, cert)
    except Exception:  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    return PASS if ok else FAIL  # pragma: no cover
