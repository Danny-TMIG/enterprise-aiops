"""Boolean -> CD embedding. NAND lifts cleanly at every level."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.cd_nand.cayley import CD, cd_from
from app.cd_nand.nand import NAND


@dataclass
class LogicalAtom:
    value: bool
    cd: CD
    level: int


@dataclass
class BooleanAlgebra:
    nand: Callable[[bool, bool], bool] = staticmethod(NAND)


def nand_to_cd(b: bool, level: int = 0) -> CD:
    """Embed a Boolean into a CD element at `level`."""
    return cd_from(b, level)


def cd_to_truth(cd: CD) -> bool:
    """Read the Boolean back out of the CD element.

    The embedding places the Boolean at the hi-most position
    recursively. `hi` at every level is either a CD or, at level 0,
    a Boolean scalar.
    """
    cur = cd
    while cur.level > 0:
        cur = cur.hi
    return bool(cur.hi)


def truth_to_cd(b: bool, level: int) -> CD:
    return cd_from(b, level)


def nand_cd(a: CD, b: CD) -> CD:
    """Lift NAND to the CD carrier at the shared level."""
    if a.level != b.level:
        raise ValueError(f"level mismatch: {a.level} vs {b.level}")
    va = cd_to_truth(a)
    vb = cd_to_truth(b)
    v = NAND(va, vb)
    return cd_from(v, a.level)


def verify_embedding(level: int = 4) -> dict:
    """Check that all four NAND pairs survive the embedding."""
    ok = True
    for a in (False, True):
        for b in (False, True):
            ca = cd_from(a, level)
            cb = cd_from(b, level)
            cc = nand_cd(ca, cb)
            if cd_to_truth(cc) != NAND(a, b):
                ok = False
    return {"level": level, "all_four_nand_pairs_match": ok}
