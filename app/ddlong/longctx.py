"""Long-context accumulation in double-double.

A sequence of N float64 samples summed naively drifts by O(N * eps
* magnitude). Using DD arithmetic the drift drops by ~30 bits of
magnitude, so a sequence of millions of samples stays accurate to
the last bit of a single float64.

This is what lets a hopping schedule run for hours without the
phase reference drifting.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from app.ddlong.dd import DD


@dataclass
class LongAccumulator:
    """Numerically stable sum of a long sequence."""
    sum: DD = field(default_factory=lambda: DD(0.0, 0.0))
    count: int = 0
    min: DD = field(default_factory=lambda: DD(float("inf"), 0.0))
    max: DD = field(default_factory=lambda: DD(float("-inf"), 0.0))

    def add(self, x) -> LongAccumulator:
        xd = x if isinstance(x, DD) else DD.from_float(float(x))
        self.sum = self.sum + xd
        self.count += 1
        self.min = min(self.min, xd)
        self.max = max(self.max, xd)
        return self

    def mean(self) -> DD:
        if self.count == 0:
            return DD(0.0, 0.0)
        return self.sum / DD.from_int(self.count)

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "sum_hi": self.sum.hi,
            "sum_lo": self.sum.lo,
            "mean_hi": self.mean().hi,
            "min_hi": self.min.hi,
            "max_hi": self.max.hi,
        }


def fold_sequence(samples: Iterable[float]) -> LongAccumulator:
    acc = LongAccumulator()
    for x in samples:
        acc.add(x)
    return acc


def phase_drift(samples: Iterable[float], drift_rate: float = 1e-16
                ) -> dict:
    """Measure the difference between naive and DD accumulation.

    Emits the residual after N samples — the amount of accumulated
    error that the naive float64 sum carries but DD does not.
    """
    naive = 0.0
    dd = DD(0.0, 0.0)
    n = 0
    for x in samples:
        naive += x
        dd = dd + DD.from_float(x)
        n += 1
    return {
        "n": n,
        "naive": naive,
        "dd_hi": dd.hi,
        "dd_lo": dd.lo,
        "residual": (dd.hi - naive),
        "residual_rel": abs((dd.hi - naive) / dd.hi) if dd.hi != 0 else 0.0,
    }
