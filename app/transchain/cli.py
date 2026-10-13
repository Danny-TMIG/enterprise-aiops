"""Demonstrate the full trans-chain lattice."""
from __future__ import annotations

import sys

from app.transchain.atoms import letters
from app.transchain.chain import Chain
from app.transchain.crisscross import cross_all, zigzag
from app.transchain.gen import (
    P,
    all_chains,
    chains_a_to_z,
    chains_of_length,
    counts,
    total_count,
)
from app.transchain.trans import trans_all


def _hdr(t: str) -> None:
    print("=" * 68)
    print(f"  {t}")
    print("=" * 68)


def _counts_table(n: int) -> None:
    _hdr(f"counts for alphabet of size {n}")
    c = counts(n)
    running = 0
    for k, v in c.items():
        running += v
        print(f"  depth {k:2d}: P({n},{k}) = {v:>25,d}    running={running:>25,d}")
    print(f"  total: {total_count(n):>25,d}")
    print()


def _full_26_table() -> None:
    _hdr("full A..Z  (26 letters)")
    c = counts(26)
    for k in (1, 2, 3, 4, 5, 6, 7, 8, 13, 20, 26):
        print(f"  depth {k:2d}: {c[k]:>32,d}")
    print(f"  total: {total_count(26):>32,d}")
    print(f"  26!  = {P(26, 26):>32,d}")
    print("  note: only depths up to ~8 are enumerable in finite time.")
    print("        all depths are countable, generatable, traversable.")
    print()


def _demo_small() -> None:
    alpha = letters(4)  # A B C D
    _hdr(f"small alphabet: {alpha}")
    print(f"  A alone                         = {Chain(('A',))}")
    print(f"  A -> B                          = "
          f"{Chain(('A','B'))}")
    print(f"  A -> B -> C                     = "
          f"{Chain(('A','B','C'))}")
    print(f"  A -> B -> C -> D                = "
          f"{Chain(('A','B','C','D'))}")
    print()

    for k in range(1, len(alpha) + 1):
        cs = list(chains_of_length(k, alpha))
        print(f"  depth {k}: {len(cs)} chains")
        for c in cs[:8]:
            print(f"    {c}")
        if len(cs) > 8:
            print(f"    ... and {len(cs)-8} more")
    print()


def _demo_a_to_z() -> None:
    alpha = letters(5)  # A B C D E
    _hdr("A -> Z with a 5-letter alphabet (A B C D E)")
    for k in range(2, 6):
        cs = list(chains_a_to_z(k, alpha))
        print(f"  depth {k}: {len(cs)} chains from A to E")
        for c in cs[:6]:
            print(f"    {c}")
        if len(cs) > 6:
            print(f"    ... and {len(cs)-6} more")
    print()


def _demo_crisscross() -> None:
    _hdr("criss-cross: zigzag interleave")
    c1 = Chain(('A', 'B', 'C'))
    c2 = Chain(('X', 'Y', 'Z'))
    print(f"  zigzag({c1}, {c2}) = {zigzag(c1, c2)}")
    c3 = Chain(('A', 'D'))
    c4 = Chain(('B', 'A', 'E'))   # shares A
    print(f"  zigzag({c3}, {c4}) = {zigzag(c3, c4)}  (A deduplicated)")
    print()

    alpha = letters(3)  # A B C
    chains = list(all_chains(alpha))
    print(f"  alphabet {alpha}, {len(chains)} chains")
    crossed = cross_all(chains)
    print(f"  distinct zigzags: {len(crossed)}")
    for c in crossed[:12]:
        print(f"    {c}")
    if len(crossed) > 12:
        print(f"    ... and {len(crossed)-12} more")
    print()


def _demo_trans() -> None:
    _hdr("trans-all: prefix-extension DAG and its closure")
    alpha = letters(4)
    info = trans_all(alpha)
    print(f"  alphabet:             {info['alphabet']}")
    print(f"  nodes (chains):       {info['nodes']}")
    print(f"  edges (prefix + 1):   {info['edges']}")
    print(f"  transitive pairs:     {info['transitive_pairs']}")
    print(f"  chains from A:        {info['chains_from_A']}")
    print(f"  chains to   D:        {info['chains_to_Z']}")
    print(f"  chains A -> D:        {info['chains_A_to_Z']}")
    print()
    print(f"  by depth: {info['by_len']}")
    print()

    print("  from (A,) to (A,B,C,D) — every step is a prefix extension:")
    cur = Chain(('A',))
    target = Chain(('A', 'B', 'C', 'D'))
    while cur.id != target.id:
        print(f"    {cur}")
        for x in target.seq:
            if x not in cur.seq:
                cur = cur.extend(x)
                break
    print(f"    {cur}   (reached)")
    print()


def main() -> int:
    _counts_table(4)
    _full_26_table()
    _demo_small()
    _demo_a_to_z()
    _demo_crisscross()
    _demo_trans()
    print("=" * 68)
    print("  A -> Z through every alphabet, every depth, every criss-cross.")
    print("  26! chains are not materializable; they are countable,")
    print("  generatable, and traversable. That is the whole lattice.")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
