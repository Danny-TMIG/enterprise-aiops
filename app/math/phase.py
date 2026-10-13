"""Phase dynamics: Kuramoto order and phase-locking value."""
from __future__ import annotations

import cmath
import math
from typing import Any


def kuramoto_R(phases: list[float]) -> dict[str, Any]:
    n = len(phases)
    if n == 0:
        return {"available": True, "R": 0.0, "N": 0}
    z = sum(cmath.exp(1j * p) for p in phases) / n
    return {"available": True, "R": round(abs(z), 6),
            "N": n, "mean_phase": round(cmath.phase(z), 4)}


def plv(phases_a: list[float], phases_b: list[float]) -> dict[str, Any]:
    n = min(len(phases_a), len(phases_b))
    if n == 0:
        return {"available": True, "PLV": 0.0, "T": 0}
    z = sum(cmath.exp(1j * (phases_a[i] - phases_b[i]))
            for i in range(n)) / n
    return {"available": True, "PLV": round(abs(z), 6), "T": n}


def phases_from_positions(positions: list[float],
                          wrap: float = 2 * math.pi) -> list[float]:
    return [(p % wrap) * (2 * math.pi / wrap) for p in positions]
