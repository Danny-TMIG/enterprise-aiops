"""NAND logic — the level-0 atom.

Every Boolean is expressed with NAND only. The other gates are
derived, not primitive. This is the seed of the Cayley-Dickson
tower: at every doubling level, the atom at the base stays NAND.
"""
from __future__ import annotations

from collections.abc import Iterable


def NAND(a: bool, b: bool) -> bool:
    return not (a and b)


def NOT(a: bool) -> bool:
    return NAND(a, a)


def AND(a: bool, b: bool) -> bool:
    return NAND(NAND(a, b), NAND(a, b))


def OR(a: bool, b: bool) -> bool:
    return NAND(NAND(a, a), NAND(b, b))


def XOR(a: bool, b: bool) -> bool:
    n_ab = NAND(a, b)
    return NAND(NAND(a, n_ab), NAND(b, n_ab))


def IMPLIES(a: bool, b: bool) -> bool:
    return OR(NOT(a), b)


def ALL(xs: Iterable[bool]) -> bool:
    acc = True
    for x in xs:
        acc = AND(acc, x)
    return acc


def ANY(xs: Iterable[bool]) -> bool:
    acc = False
    for x in xs:
        acc = OR(acc, x)
    return acc


# ── truth-table exhaustiveness check ────────────────────────────
def exhaustive_check() -> dict:
    """Assert that the NAND-derived gates match their standard
    truth tables over every input."""
    ok = True
    for a in (False, True):
        for b in (False, True):
            if NOT(a) != (not a): ok = False
            if AND(a, b) != (a and b): ok = False
            if OR(a, b) != (a or b): ok = False
            if XOR(a, b) != (a != b): ok = False
            if IMPLIES(a, b) != ((not a) or b): ok = False
    return {"all_gates_match_standard_truth_tables": ok,
            "atom": "NAND(a, b) = not (a and b)"}
