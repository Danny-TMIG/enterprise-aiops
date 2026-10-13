"""Criss-cross: zigzag interleave of two chains.

Given c1 = a1 a2 a3 ... and c2 = b1 b2 b3 ...,
zigzag(c1, c2) = a1 b1 a2 b2 a3 b3 ...

If the two chains share a letter, the shared letter is emitted once.
Length = |c1| + |c2| - shared_count.
"""
from __future__ import annotations

from collections.abc import Iterator

from app.transchain.chain import Chain


def zigzag(c1: Chain, c2: Chain) -> Chain:
    out: list[str] = []
    seen = set()
    i = j = 0
    while i < len(c1) or j < len(c2):
        if i < len(c1):
            x = c1.seq[i]
            if x not in seen:
                out.append(x); seen.add(x)
            i += 1
        if j < len(c2):
            y = c2.seq[j]
            if y not in seen:
                out.append(y); seen.add(y)
            j += 1
    return Chain(tuple(out))


def criss_cross(chains: list[Chain]
                ) -> Iterator[tuple[Chain, Chain, Chain]]:
    """For every ordered pair (c1, c2), yield (c1, c2, zigzag(c1, c2))."""
    for c1 in chains:
        for c2 in chains:
            yield (c1, c2, zigzag(c1, c2))


def cross_all(chains: list[Chain]) -> list[Chain]:
    """The set of distinct zigzags across every ordered pair."""
    seen = set()
    out: list[Chain] = []
    for c1 in chains:
        for c2 in chains:
            z = zigzag(c1, c2)
            if z.id not in seen:
                seen.add(z.id)
                out.append(z)
    return out
