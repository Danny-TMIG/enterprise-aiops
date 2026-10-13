"""Cayley-Dickson doubling over an arbitrary base algebra."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


# ── Alg: the operations on a carrier ────────────────────────────
@dataclass
class Alg:
    add: Callable[[Any, Any], Any]
    sub: Callable[[Any, Any], Any]
    mul: Callable[[Any, Any], Any]
    neg: Callable[[Any], Any]
    conj: Callable[[Any], Any]
    is_zero: Callable[[Any], bool]
    zero: Any
    one: Any
    name: str = "?"


# ── CD element at level k ───────────────────────────────────────
@dataclass(frozen=True)
class CD:
    """A Cayley-Dickson element at level `level`.

    Invariant: `hi` and `lo` are either both the base scalar (level 0)
    or both CDs at level `level - 1`. `op` is the level-`level`
    algebra descriptor.
    """
    hi: Any
    lo: Any
    level: int
    op: Alg

    def __add__(self, other: CD) -> CD:
        return CD(self.op.add(self.hi, other.hi),
                  self.op.add(self.lo, other.lo),
                  level=self.level, op=self.op)

    def __sub__(self, other: CD) -> CD:
        return CD(self.op.sub(self.hi, other.hi),
                  self.op.sub(self.lo, other.lo),
                  level=self.level, op=self.op)

    def __neg__(self) -> CD:
        return CD(self.op.neg(self.hi), self.op.neg(self.lo),
                  level=self.level, op=self.op)

    def conj(self) -> CD:
        """(a, b)* = (a*, -b)"""
        return CD(self.op.conj(self.hi), self.op.neg(self.lo),
                  level=self.level, op=self.op)

    def __mul__(self, other: CD) -> CD:
        """(a, b)(c, d) = (a c - d* b,  d a + b c*)"""
        a, b = self.hi, self.lo
        c, d = other.hi, other.lo
        # Conjugation must be routed through self.op.conj because at
        # level 0 the operands are raw scalars (bool) that have no
        # `.conj()` method. BOOL_ALG.conj is the identity; higher
        # levels' op.conj composes down the tower.
        hi = self.op.sub(self.op.mul(a, c),
                         self.op.mul(self.op.conj(d), b))
        lo = self.op.add(self.op.mul(d, a),
                         self.op.mul(b, self.op.conj(c)))
        return CD(hi, lo, level=self.level, op=self.op)

    def is_zero(self) -> bool:
        return self.op.is_zero(self.hi) and self.op.is_zero(self.lo)

    def __repr__(self) -> str:
        return f"CD(L{self.level}|{self.hi!r},{self.lo!r})"


# ── base Boolean algebra (level 0) ──────────────────────────────
BOOL_ALG = Alg(
    add=lambda a, b: a != b,          # XOR = addition in GF(2)
    sub=lambda a, b: a != b,          # subtraction = addition in GF(2)
    mul=lambda a, b: a and b,
    neg=lambda a: a,                  # -x = x in GF(2)
    conj=lambda a: a,
    is_zero=lambda a: not a,
    zero=False,
    one=True,
    name="bool",
)


# ── build an Alg for level k from an Alg for level k-1 ──────────
def _recursive_alg(inner: Alg, level: int) -> Alg:
    """Alg whose carrier is CD-at-(level-1)."""
    def add(x, y): return x + y
    def sub(x, y): return x - y
    def mul(x, y): return x * y
    def neg(x): return -x
    def conj(x): return x.conj()
    def is_zero(x): return x.is_zero()

    zero = CD(inner.zero, inner.zero, level=level - 1, op=inner)
    one = CD(inner.one, inner.zero, level=level - 1, op=inner)

    return Alg(add=add, sub=sub, mul=mul, neg=neg, conj=conj,
               is_zero=is_zero, zero=zero, one=one,
               name=f"cd-L{level}")


_ALG_CACHE: dict = {0: BOOL_ALG}


def alg_at(level: int) -> Alg:
    """Return the algebra descriptor for a CD element at `level`."""
    if level in _ALG_CACHE:
        return _ALG_CACHE[level]
    if level < 0:
        raise ValueError(f"level must be >= 0, got {level}")
    inner = alg_at(level - 1)
    a = _recursive_alg(inner, level)
    _ALG_CACHE[level] = a
    return a


def cd_from(value: Any, level: int = 0) -> CD:
    """Embed a scalar (Boolean, by default) into a level-`level` CD.

    At level 0: value at hi, zero at lo.
    At level k>0: nested k times.
    """
    if level == 0:
        return CD(value, BOOL_ALG.zero, level=0, op=BOOL_ALG)
    inner = cd_from(value, level - 1)
    zero_inner = cd_from(BOOL_ALG.zero, level - 1)
    return CD(inner, zero_inner, level=level, op=alg_at(level))


def cd_zero(level: int = 0) -> CD:
    return cd_from(BOOL_ALG.zero, level)


def cd_one(level: int = 0) -> CD:
    return cd_from(BOOL_ALG.one, level)


def cd_basis(n: int) -> list:
    """2^n basis elements of the level-n CD algebra.

    e_k has a single 1 at position k (indexed by the natural
    left-to-right embedding) and 0 elsewhere.
    """
    if n == 0:
        return [cd_from(True, 0)]
    half = cd_basis(n - 1)
    zeros = [cd_zero(n - 1)]
    left = [CD(h, zeros[0], level=n, op=alg_at(n)) for h in half]
    right = [CD(zeros[0], h, level=n, op=alg_at(n)) for h in half]
    return left + right
