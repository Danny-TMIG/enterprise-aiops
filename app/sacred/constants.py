"""The four constants that survive.

PHI       golden ratio          (1 + sqrt(5)) / 2 = 1.6180339887...
PHI_INV   1 / PHI = PHI - 1    0.6180339887...
PHI_SQ    PHI + 1 = PHI^2       2.6180339887...
SILVER    1 - PHI = -PHI_INV    the conjugate root

The defining identity:  PHI^2 = PHI + 1
Equivalently:           PHI_INV^2 = 1 - PHI_INV
"""
from __future__ import annotations

import math
from functools import cache

PHI: float = (1.0 + math.sqrt(5.0)) / 2.0     # 1.6180339887498949
PHI_INV: float = PHI - 1.0                    # 0.6180339887498949
PHI_SQ: float = PHI + 1.0                     # 2.6180339887498949
SILVER_RATIO: float = 1.0 - PHI               # -0.6180339887498949

assert abs(PHI * PHI - (PHI + 1.0)) < 1e-15
assert abs(PHI_INV * PHI - 1.0) < 1e-15
assert abs(PHI_INV * PHI_INV - (1.0 - PHI_INV)) < 1e-15


# ── Fibonacci ──────────────────────────────────────────────────
@cache
def fib(n: int) -> int:
    """The n-th Fibonacci number, F(0)=0, F(1)=1."""
    if n < 0:
        raise ValueError("n must be >= 0")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_seq(n: int) -> list[int]:
    """[F(0), F(1), ..., F(n)]."""
    return [fib(k) for k in range(n + 1)]


def fib_ge(target: int) -> int:
    """Smallest k with F(k) >= target."""
    k = 0
    while fib(k) < target:
        k += 1
    return k


FIBONACCI: tuple = tuple(fib(k) for k in range(40))


# ── the closure identity ──────────────────────────────────────
def check_closure(x: float, tol: float = 1e-12) -> bool:
    """The golden closure: x = 1/x + 1 has exactly one positive
    root and it is PHI. This is why Fibonacci-type sequences
    converge to PHI regardless of initial seed."""
    return abs(x - (1.0 / x + 1.0)) < tol
