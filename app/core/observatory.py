"""Observatory: run a phenomenon and record its trajectory.

A snapshot is not a phenomenon. A curve is. This module wraps any
object that has tick() and topology() (or any callable that returns
a dict) and records the values of named keys across ticks.

Self-registers as capability `observatory`.
"""
from __future__ import annotations

import statistics
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Trajectory:
    code: str
    steps: int
    series: dict[str, list[float]] = field(default_factory=dict)
    scalars: dict[str, Any] = field(default_factory=dict)

    def stats(self, key: str) -> dict[str, float]:
        xs = self.series.get(key, [])
        if not xs:
            return {}
        return {
            "n": len(xs),
            "first": xs[0],
            "last": xs[-1],
            "min": min(xs),
            "max": max(xs),
            "mean": statistics.fmean(xs),
            "stdev": statistics.pstdev(xs) if len(xs) > 1 else 0.0,
            "range": max(xs) - min(xs),
        }

    def rate(self, key: str) -> float:
        """Per-step drift: (last - first)/steps."""
        xs = self.series.get(key, [])
        if len(xs) < 2:
            return 0.0
        return (xs[-1] - xs[0]) / (len(xs) - 1)

    def criticality(self, key: str) -> float:
        """Variance / mean^2. High near a phase transition."""
        xs = self.series.get(key, [])
        if not xs:
            return 0.0
        m = statistics.fmean(xs)
        if abs(m) < 1e-12:
            return 0.0
        v = statistics.pvariance(xs)
        return v / (m * m)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "steps": self.steps,
            "series": {k: [round(x, 6) for x in v] for k, v in self.series.items()},
            "scalars": self.scalars,
        }


# ── wrap a PhysarumRouter (or anything with tick/topology) ──────────
def observe_live(obj: Any, steps: int, *,
                 extract: Callable[[Any], dict[str, float]] | None = None,
                 sample_every: int = 1) -> Trajectory:
    """Run obj.tick(1) `steps` times. After each tick, call extract(obj)
    and record its dict. Default extractor understands PhysarumRouter
    and any object with .stats() or .topology()."""
    if extract is None:
        extract = _default_extract
    tr = Trajectory(code=obj.__class__.__name__, steps=steps)
    for i in range(steps):
        if hasattr(obj, "tick"):
            obj.tick(1)
        if i % sample_every == 0 or i == steps - 1:
            snap = extract(obj) or {}
            for k, v in snap.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    tr.series.setdefault(k, []).append(float(v))
    return tr


def _default_extract(obj: Any) -> dict[str, float]:
    out: dict[str, float] = {}
    if hasattr(obj, "topology"):
        try:
            top = obj.topology()
            for k, v in top.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    out[k] = float(v)
        except Exception:
            pass
    if hasattr(obj, "stats"):
        try:
            st = obj.stats()
            for k, v in st.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    out[k] = float(v)
        except Exception:
            pass
    # PhysarumRouter-specific: capture D distribution summary
    if hasattr(obj, "edges"):
        try:
            edges = list(obj.edges(include_pruned=False))
            if edges:
                ds = [e.D for e in edges]
                out["D_mean"] = statistics.fmean(ds)
                out["D_max"] = max(ds)
                out["D_min"] = min(ds)
                out["edges_live"] = float(len(edges))
            all_e = list(obj.edges(include_pruned=True))
            pruned = sum(1 for e in all_e if e.pruned)
            out["edges_pruned"] = float(pruned)
        except Exception:
            pass
    return out


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("observatory")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "module": "app.core.observatory",
            "classes": ["Trajectory"],
            "functions": ["observe_live"],
        }


_self_register()


__all__ = ["Trajectory", "observe_live"]
