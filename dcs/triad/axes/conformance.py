"""Conformance: does the artifact match its declaration?"""
from __future__ import annotations
from typing import Any, Callable, Iterable
from dcs.triad.lattice import VState, PASS, FAIL, UNKNOWN


def resolve(declared: Any, actual: Any, *,
            compare: Callable[[Any, Any], bool] | None = None) -> VState:
    if compare is None:
        compare = lambda d, a: d == a
    try:
        return PASS if compare(declared, actual) else FAIL
    except Exception:
        return UNKNOWN


def schema(declared_fields: set, actual_fields: set) -> VState:
    if not declared_fields:
        return UNKNOWN
    return PASS if set(actual_fields) >= set(declared_fields) else FAIL


def behavioral(pred: Callable[[Any], bool], sample: Iterable[Any], *,
               epsilon: float = 1e-9) -> VState:
    s = list(sample)
    if not s:
        return UNKNOWN
    k = sum(1 for x in s if pred(x))
    if k == len(s):
        return PASS
    if k == 0:
        return FAIL
    rate = k / len(s)
    if abs(rate - 0.5) < epsilon:
        return FAIL
    return UNKNOWN


def certificate(claim: dict, cert: dict, *,
                verifier: Callable[[dict, dict], bool]) -> VState:
    try:
        ok = verifier(claim, cert)
    except Exception:
        return UNKNOWN
    return PASS if ok else FAIL
