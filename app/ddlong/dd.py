"""Double-double arithmetic.

A DD is a pair (hi, lo) of float64 such that hi + lo approximates
the intended value with ~106 bits of mantissa (~31 decimal digits)
instead of the 53 bits of a single float64.

Uses Dekker's error-free transformations:
  TwoSum(a, b)  -> (s, e) with a+b = s+e exactly
  TwoProd(a, b) -> (p, e) with a*b = p+e exactly

Reference: Bailey, "High-Precision Floating-Point Arithmetic in
Scientific Computation", 2005.
"""
from __future__ import annotations

from dataclasses import dataclass


def two_sum(a: float, b: float) -> tuple[float, float]:
    s = a + b
    bb = s - a
    e = (a - (s - bb)) + (b - bb)
    return s, e


def quick_two_sum(a: float, b: float) -> tuple[float, float]:
    s = a + b
    e = b - (s - a)
    return s, e


def split(a: float) -> tuple[float, float]:
    """Split a into (hi, lo) each holding <= 26 bits of mantissa."""
    c = 134217729.0 * a           # 2**27 + 1
    hi = c - (c - a)
    lo = a - hi
    return hi, lo


def two_prod(a: float, b: float) -> tuple[float, float]:
    p = a * b
    ah, al = split(a)
    bh, bl = split(b)
    e = ((ah * bh - p) + ah * bl + al * bh) + al * bl
    return p, e


@dataclass(frozen=True)
class DD:
    hi: float = 0.0
    lo: float = 0.0

    # ── normalisation ──────────────────────────────────────────
    @staticmethod
    def normalise(hi: float, lo: float) -> DD:
        s, e = quick_two_sum(hi, lo)
        return DD(s, e)

    # ── constructors ───────────────────────────────────────────
    @staticmethod
    def from_float(x: float) -> DD:
        return DD(x, 0.0)

    @staticmethod
    def from_int(x: int) -> DD:
        return DD(float(x), 0.0)

    # ── arithmetic ─────────────────────────────────────────────
    def __add__(self, other) -> DD:
        o = other if isinstance(other, DD) else DD.from_float(float(other))
        s1, s2 = two_sum(self.hi, o.hi)
        t1, t2 = two_sum(self.lo, o.lo)
        s2 += t1
        s1, s2 = quick_two_sum(s1, s2)
        s2 += t2
        s1, s2 = quick_two_sum(s1, s2)
        return DD(s1, s2)

    def __radd__(self, other) -> DD:
        return self.__add__(other)

    def __neg__(self) -> DD:
        return DD(-self.hi, -self.lo)

    def __sub__(self, other) -> DD:
        o = other if isinstance(other, DD) else DD.from_float(float(other))
        return self + (-o)

    def __rsub__(self, other) -> DD:
        return DD.from_float(float(other)) - self

    def __mul__(self, other) -> DD:
        o = other if isinstance(other, DD) else DD.from_float(float(other))
        p1, p2 = two_prod(self.hi, o.hi)
        p2 += self.hi * o.lo
        p2 += self.lo * o.hi
        p1, p2 = quick_two_sum(p1, p2)
        return DD(p1, p2)

    def __rmul__(self, other) -> DD:
        return self.__mul__(other)

    def __truediv__(self, other) -> DD:
        o = other if isinstance(other, DD) else DD.from_float(float(other))
        q1 = self.hi / o.hi
        r = self - o * DD.from_float(q1)
        q2 = r.hi / o.hi
        r = r - o * DD.from_float(q2)
        q3 = r.hi / o.hi
        return (DD.from_float(q1) + DD.from_float(q2)) + DD.from_float(q3)

    def __pow__(self, n: int) -> DD:
        if n < 0:
            return DD(1.0, 0.0) / (self ** (-n))
        result = DD(1.0, 0.0)
        base = self
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result

    # ── comparisons / conversions ─────────────────────────────
    def __float__(self) -> float:
        return self.hi

    def to_float(self) -> float:
        return self.hi

    def __abs__(self) -> DD:
        return DD(abs(self.hi), abs(self.lo)) if self.hi >= 0 else -self

    def __eq__(self, other) -> bool:
        o = other if isinstance(other, DD) else DD.from_float(float(other))
        return self.hi == o.hi and self.lo == o.lo

    def __lt__(self, other) -> bool:
        o = other if isinstance(other, DD) else DD.from_float(float(other))
        if self.hi != o.hi:
            return self.hi < o.hi
        return self.lo < o.lo

    def __repr__(self) -> str:
        return f"DD({self.hi!r}, {self.lo!r})"

    def __str__(self) -> str:
        return f"{self.hi:.17g} + {self.lo:+.3e}"


def dd_from_float(x: float) -> DD:
    return DD.from_float(x)
