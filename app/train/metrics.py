"""Non-static floating point metrics.

The problem with a static metric: rate = passes/trials is the same
number every generation if the puzzles are the same. To make it
move, three things must vary:

    1. the puzzle seed (so instances differ)
    2. the window (so the metric forgets old data)
    3. the DD accumulator (so drift does not eat the signal)

Metrics here:

    EWMA            exponentially weighted moving average
    Window          sliding window of the last K rates
    FirstDiff       x[t] - x[t-1]            (velocity)
    SecondDiff      (x[t]-x[t-1]) - (x[t-1]-x[t-2])  (acceleration)
    Entropy         Shannon entropy of the pass/fail distribution
    Drift           DD-accumulated phase drift of the metric stream

Every float is stored at DD precision when accumulated over many
generations. Single-generation values are float64.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.ddlong.dd import DD


# ── EWMA ────────────────────────────────────────────────────────
@dataclass
class EWMA:
    # α = PHI_INV = 0.618 is the unique α for which
    # α = 1 - α², so the EWMA window is Fibonacci-proportional
    # and its half-life is exactly one Fibonacci step.
    alpha: float = 0.6180339887498949
    value: float | None = None
    samples: int = 0

    def push(self, x: float) -> float:
        if self.value is None:
            self.value = x
        else:
            self.value = self.alpha * x + (1 - self.alpha) * self.value
        self.samples += 1
        return self.value


# ── sliding window ──────────────────────────────────────────────
@dataclass
class Window:
    k: int = 4
    buf: list[float] = field(default_factory=list)

    def push(self, x: float) -> float:
        self.buf.append(x)
        if len(self.buf) > self.k:
            self.buf.pop(0)
        return self.mean()

    def mean(self) -> float:
        return sum(self.buf) / len(self.buf) if self.buf else 0.0

    def std(self) -> float:
        if len(self.buf) < 2:
            return 0.0
        m = self.mean()
        var = sum((x - m) ** 2 for x in self.buf) / (len(self.buf) - 1)
        return math.sqrt(var)


# ── derivative tracker ──────────────────────────────────────────
@dataclass
class Derivatives:
    last: float | None = None
    prev_diff: float | None = None

    def push(self, x: float) -> tuple[float, float]:
        if self.last is None:
            self.last = x
            return 0.0, 0.0
        d1 = x - self.last
        d2 = d1 - (self.prev_diff if self.prev_diff is not None else 0.0)
        self.prev_diff = d1
        self.last = x
        return d1, d2


# ── entropy over pass/fail counts ───────────────────────────────
def binary_entropy(passes: int, fails: int) -> float:
    total = passes + fails
    if total == 0:
        return 0.0
    p = passes / total
    q = 1 - p
    if p == 0 or q == 0:
        return 0.0
    return -(p * math.log2(p) + q * math.log2(q))


# ── DD phase drift tracker ──────────────────────────────────────
@dataclass
class DriftTracker:
    ref: DD = field(default_factory=lambda: DD(0.0, 0.0))
    n: int = 0

    def push(self, x: float) -> tuple[float, float]:
        self.ref = self.ref + DD.from_float(x)
        self.n += 1
        return self.ref.hi, self.ref.lo


# ── the metric stream ───────────────────────────────────────────
@dataclass
class StreamMetrics:
    """One non-static metric per (kind, solver).

    Every push updates: EWMA, window, first/second difference,
    entropy, and DD phase drift. All five values evolve as the
    stream progresses. No metric is the same as the previous
    generation unless the underlying rate is genuinely fixed.
    """
    kind: str
    solver: str
    ewma: EWMA = field(default_factory=EWMA)
    window: Window = field(default_factory=Window)
    deriv: Derivatives = field(default_factory=Derivatives)
    drift: DriftTracker = field(default_factory=DriftTracker)
    passes_total: int = 0
    fails_total: int = 0
    history: list[dict[str, float]] = field(default_factory=list)

    def push(self, passes: int, trials: int) -> dict[str, float]:
        """Push a whole-generation tile: pushes each of the `trials`
        individual outcomes into the moving-average stream first,
        then records the generation snapshot.

        This is what makes the metric non-static even when the
        per-tile rate is fixed: an EWMA over individual puzzle
        outcomes sees each pass/fail, not the mean.
        """
        # push each individual outcome into the raw streams
        for i in range(trials):
            individual = 1.0 if i < passes else 0.0
            self.ewma.push(individual)
            self.window.push(individual)
            self.deriv.push(individual)
            self.drift.push(individual)

        rate = passes / trials if trials else 0.0
        self.passes_total += passes
        self.fails_total += trials - passes

        ent = binary_entropy(passes, trials - passes)
        hi = self.drift.ref.hi
        lo = self.drift.ref.lo

        snap = {
            "gen": len(self.history),
            "rate": rate,
            "ewma": self.ewma.value if self.ewma.value is not None else 0.0,
            "window_mean": self.window.mean(),
            "window_std": self.window.std(),
            "d1": self.deriv.prev_diff if self.deriv.prev_diff is not None else 0.0,
            "d2": 0.0,
            "entropy": ent,
            "drift_hi": hi,
            "drift_lo": lo,
            "raw_samples": self.ewma.samples,
        }
        self.history.append(snap)
        return snap

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "solver": self.solver,
            "n": len(self.history),
            "latest": self.history[-1] if self.history else None,
            "series_rate": [h["rate"] for h in self.history],
            "series_ewma": [h["ewma"] for h in self.history],
            "series_d1": [h["d1"] for h in self.history],
            "series_d2": [h["d2"] for h in self.history],
            "series_entropy": [h["entropy"] for h in self.history],
        }


class MetricsRegistry:
    """Per (kind, solver, difficulty) streams.

    The key includes difficulty so that a solver at easy and a
    solver at hard are two separate non-static metric streams.
    A merged stream would average out the variation and look
    static even when the underlying rate moves.
    """
    def __init__(self):
        self.streams: dict[tuple[str, str, str], StreamMetrics] = {}

    def push(self, kind: str, solver: str, difficulty: str,
             passes: int, trials: int) -> dict[str, float]:
        key = (kind, solver, difficulty)
        s = self.streams.get(key)
        if s is None:
            s = StreamMetrics(kind=f"{kind}/{difficulty}", solver=solver)
            self.streams[key] = s
        return s.push(passes, trials)

    def summary(self) -> list[dict]:
        return [s.to_dict() for s in self.streams.values()]

    def non_static(self, threshold: float = 1e-9) -> list[str]:
        out = []
        for (k, s, d), st in self.streams.items():
            rates = [h["rate"] for h in st.history]
            if len(set(rates)) > 1:
                out.append(f"{k}/{s}/{d}")
        return sorted(out)

    def static(self, threshold: float = 1e-9) -> list[str]:
        out = []
        for (k, s, d), st in self.streams.items():
            rates = [h["rate"] for h in st.history]
            if len(rates) >= 2 and len(set(rates)) == 1:
                out.append(f"{k}/{s}/{d}")
        return sorted(out)


def series_with_derivatives(history: list) -> dict:
    """Compute d1 and d2 series from the history of `rate` values."""
    rates = [h["rate"] for h in history]
    d1 = [0.0] + [rates[i] - rates[i-1] for i in range(1, len(rates))]
    d2 = [0.0] + [d1[i] - d1[i-1] for i in range(1, len(d1))]
    return {"rate": rates, "d1": d1, "d2": d2}
