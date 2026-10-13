"""Generate every chain, every depth, lazily.

For alphabet size n:
    P(n,k) = n!/(n-k)!   chains of length k
    total  = sum_{k=1..n} P(n,k)
"""
from __future__ import annotations

import math
from collections.abc import Iterator
from itertools import permutations

from app.transchain.atoms import ALPHABET
from app.transchain.chain import Chain


def P(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.factorial(n) // math.factorial(n - k)


def counts(n: int = 26) -> dict[int, int]:
    """Length k -> count of length-k chains over an n-letter alphabet."""
    return {k: P(n, k) for k in range(1, n + 1)}


def total_count(n: int = 26) -> int:
    return sum(counts(n).values())


def chains_of_length(k: int, alpha: tuple[str, ...] = ALPHABET
                     ) -> Iterator[Chain]:
    if k < 1 or k > len(alpha):
        return
    for p in permutations(alpha, k):
        yield Chain(p)


def all_chains(alpha: tuple[str, ...] = ALPHABET,
               max_len: int | None = None) -> Iterator[Chain]:
    """Every chain of every length 1..len(alpha). Lazy."""
    top = max_len if max_len is not None else len(alpha)
    for k in range(1, top + 1):
        yield from chains_of_length(k, alpha)


def chains_from(a: str, k: int, alpha: tuple[str, ...] = ALPHABET
                ) -> Iterator[Chain]:
    """Length-k chains starting at letter `a`."""
    rest = tuple(x for x in alpha if x != a)
    if k == 1:
        yield Chain((a,))
        return
    for p in permutations(rest, k - 1):
        yield Chain((a,) + p)


def chains_to(z: str, k: int, alpha: tuple[str, ...] = ALPHABET
              ) -> Iterator[Chain]:
    """Length-k chains ending at letter `z`."""
    rest = tuple(x for x in alpha if x != z)
    if k == 1:
        yield Chain((z,))
        return
    for p in permutations(rest, k - 1):
        yield Chain(p + (z,))


def chains_a_to_z(k: int, alpha: tuple[str, ...] = ALPHABET
                  ) -> Iterator[Chain]:
    """Length-k chains from A to Z."""
    a, z = alpha[0], alpha[-1]
    if k == 2:
        yield Chain((a, z))
        return
    middle = tuple(x for x in alpha if x not in (a, z))
    for p in permutations(middle, k - 2):
        yield Chain((a,) + p + (z,))
