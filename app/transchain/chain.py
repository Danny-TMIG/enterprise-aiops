"""A chain is a finite sequence of distinct letters."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Chain:
    seq: tuple[str, ...]

    def __post_init__(self):
        if not self.seq:
            raise ValueError("empty chain")
        if len(set(self.seq)) != len(self.seq):
            raise ValueError(f"repeats in chain: {self.seq}")

    def __len__(self) -> int:
        return len(self.seq)

    def __iter__(self):
        return iter(self.seq)

    def __str__(self) -> str:
        return "->".join(self.seq)

    @property
    def head(self) -> str:
        return self.seq[0]

    @property
    def tail(self) -> str:
        return self.seq[-1]

    @property
    def id(self) -> str:
        return str(self)

    def extend(self, x: str) -> Chain:
        return Chain(self.seq + (x,))

    def is_prefix_of(self, other: Chain) -> bool:
        return (len(self) <= len(other)
                and other.seq[:len(self)] == self.seq)

    def overlap(self, other: Chain) -> int:
        """Longest k such that self.seq[-k:] == other.seq[:k]."""
        k_max = min(len(self), len(other))
        for k in range(k_max, 0, -1):
            if self.seq[-k:] == other.seq[:k]:
                return k
        return 0


def chain(seq: Iterable[str]) -> Chain:
    return Chain(tuple(seq))


def is_chain(seq: Iterable[str]) -> bool:
    try:
        Chain(tuple(seq))
        return True
    except Exception:
        return False
