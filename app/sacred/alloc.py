"""Resource allocation and decay constants.

Three concrete uses:

    fib_alloc           distribute N units so that consecutive
                        tiers receive Fibonacci-proportional shares
    phi_ewma_alpha      decay constant for an EWMA; PHI_INV is the
                        unique rate whose half-life is exactly one
                        Fibonacci step
    golden_ratio_tick   a low-discrepancy sequence on [0,1):
                        frac(k * PHI_INV).  Unlike random, no two
                        successive points cluster.
"""
from __future__ import annotations

from app.sacred.constants import PHI_INV, fib


def fib_alloc(total: int, tiers: int = 5) -> list[int]:
    """Partition `total` into `tiers` buckets following Fibonacci
    proportions. Largest bucket at the top tier (closest to the
    action), smallest at the leaves. Sum is preserved exactly."""
    if tiers < 1:
        raise ValueError("tiers >= 1")
    weights = [fib(tiers - i) for i in range(tiers)]   # F(t), F(t-1), ...
    wsum = sum(weights)
    out = [total * w // wsum for w in weights]
    # distribute the remainder to the first bucket
    rem = total - sum(out)
    out[0] += rem
    return out


def phi_ewma_alpha() -> float:
    """The α for EWMA such that α = 1 - α².  Root: α = PHI_INV.
    This is the only α for which an EWMA's smoothed value is the
    weighted average of a Fibonacci-proportional window."""
    return PHI_INV


def golden_ratio_tick(k: int) -> float:
    """{k * PHI_INV} for integer k.  A 2-D version,
    ({k * PHI_INV}, {k * PHI_INV^2}), is a low-discrepancy
    sequence on the unit square — the same construction used
    for phyllotaxis (leaf arrangement)."""
    return (k * PHI_INV) % 1.0


def golden_tick_2d(k: int) -> tuple:
    """The 2-D golden tick: ({k * φ⁻¹}, {k * φ⁻²}).  Same as
    `phyllotaxis(k)` in geometry.py but expressed without the
    spiral radius.  Use phyllotaxis() for disk packing, this for
    plain [0,1)^2 low-discrepancy points."""
    return ((k * PHI_INV) % 1.0, (k * PHI_INV * PHI_INV) % 1.0)
