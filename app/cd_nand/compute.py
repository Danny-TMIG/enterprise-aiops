"""Real computation on the CD tower.

NAND(a,b) = NOT(a AND b).
In GF(2):  a AND b = a*b (multiplication).
           NOT(x)  = x + 1 (addition with True = XOR).
So NAND is (a*b) + 1 using only CD mul/add at any level.

Verified exhaustively against app.cd_nand.nand.NAND.
"""
from __future__ import annotations

from app.cd_nand.cayley import cd_from
from app.cd_nand.map_to_logic import cd_to_truth


def nand_cd(a: bool, b: bool, level: int = 3) -> bool:
    x = cd_from(a, level)
    y = cd_from(b, level)
    one = cd_from(True, level)
    prod = x * y          # CD multiplication
    res = prod + one      # CD addition = XOR at level 0
    return cd_to_truth(res)

def verify_all_levels(max_level: int = 6) -> dict:
    from app.cd_nand.nand import NAND
    bad = {}
    for lvl in range(max_level + 1):
        for a in (False, True):
            for b in (False, True):
                if nand_cd(a, b, lvl) != NAND(a, b):
                    bad.setdefault(lvl, []).append((a, b))
    return {"ok": not bad, "max_level": max_level, "failures": bad}
