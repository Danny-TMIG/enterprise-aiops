"""Demonstrate the Cayley-Dickson tower over NAND."""
from __future__ import annotations

import sys

from app.cd_nand.cayley import BOOL_ALG, cd_basis
from app.cd_nand.levels import (
    full_tower,
    level_module,
)
from app.cd_nand.map_to_logic import (
    cd_to_truth,
    nand_cd,
    nand_to_cd,
    verify_embedding,
)
from app.cd_nand.nand import AND, IMPLIES, NAND, NOT, OR, XOR, exhaustive_check


def _hdr(t):
    print("=" * 72)
    print("  " + t)
    print("=" * 72)


def demo_nand():
    _hdr("L0 — NAND is the only atom")
    chk = exhaustive_check()
    print(f"  {chk['all_gates_match_standard_truth_tables']=}")
    print(f"  {chk['atom']}")
    print("  truth table:")
    for a in (False, True):
        for b in (False, True):
            print(f"    NAND({a:>1},{b:>1})={NAND(a,b):>1}  "
                  f"NOT({a:>1})={NOT(a):>1}  "
                  f"AND={AND(a,b):>1} OR={OR(a,b):>1} "
                  f"XOR={XOR(a,b):>1} IMPLIES={IMPLIES(a,b):>1}")
    print()


def demo_cd():
    _hdr("CD algebra at a small level")
    for level in (1, 2, 3):
        basis = cd_basis(BOOL_ALG, level)
        print(f"  L{level}: dim={len(basis)}  basis[:4]={basis[:4]}")
        # pick two basis elements and multiply
        if len(basis) >= 2:
            a, b = basis[1], basis[1]
            prod = a * b
            print(f"    {a!r}")
            print("    *")
            print(f"    {b!r}")
            print("    =")
            print(f"    {prod!r}")
        print()


def demo_tower():
    _hdr("the ten-level tower")
    t = full_tower()
    for s in t.summary():
        print(f"  L{s['level']}  dim={s['dim']:>4}  {s['name']:<26}  "
              f"loses: {s['loses']}")
        print(f"       primitives: {s['primitives']}")
        print(f"       invariant : {s['invariant']}")
    print()


def demo_levels():
    _hdr("per-level modules")
    for i in range(10):
        m = level_module(i)
        print(f"  L{m['level']}  {m['name']}")
        print(f"    basis size:   {len(m['basis'])}")
        print(f"    algebra:      {m['algebra'].name}")
        print(f"    {m['note']}")
    print()


def demo_embedding():
    _hdr("Boolean embedding into the CD tower")
    for level in (0, 1, 2, 4, 8):
        r = verify_embedding(level=level)
        print(f"  L{level}: {r}")
    print()
    print("  sample embedding at L4:")
    for b in (False, True):
        cd = nand_to_cd(b, level=4)
        back = cd_to_truth(cd)
        print(f"    {b}  ->  {cd!r}  ->  {back}")
    print()
    print("  lift NAND into L4:")
    for a in (False, True):
        for b in (False, True):
            ca = nand_to_cd(a, 4)
            cb = nand_to_cd(b, 4)
            cc = nand_cd(ca, cb)
            print(f"    NAND({a:>1},{b:>1}) = {NAND(a,b):>1}  "
                  f"lifted_truth={cd_to_truth(cc)}")
    print()


def main():
    demo_nand()
    demo_cd()
    demo_tower()
    demo_levels()
    demo_embedding()
    print("=" * 72)
    print("  Boolean logic is the real subalgebra of every higher CD level.")
    print("  Each doubling loses one property. The tower never closes.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
