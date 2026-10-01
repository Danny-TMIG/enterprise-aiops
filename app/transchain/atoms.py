"""A through Z. The twenty-six atoms."""
from __future__ import annotations
import string
from typing import List, Tuple

ALPHABET: Tuple[str, ...] = tuple(string.ascii_uppercase)   # A..Z


def letters(n: int | None = None) -> Tuple[str, ...]:
    """First n letters. Default: all 26."""
    if n is None:
        return ALPHABET
    if n < 1 or n > 26:
        raise ValueError("n must be in 1..26")
    return ALPHABET[:n]
