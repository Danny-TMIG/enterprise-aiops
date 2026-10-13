"""φ-based annealing schedules.

Classical simulated annealing uses T(k) = T0 * α^k with α ∈ [0.9, 0.99).
Golden Ratio Simulated Annealing (GRSA) uses α = PHI_INV ≈ 0.618.
Fibonacci cooling uses T(k) = T0 / F(k+1).

The GRSA cooling rate is a documented technique for satisfiability
problems: it reaches lower energies in fewer iterations than the
classical schedule because the ratio between consecutive
temperatures is the slowest-converging ratio of any Fibonacci-type
sequence.
"""
from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass, field

from app.sacred.constants import PHI_INV, fib


@dataclass
class CoolingTrace:
    schedule: str
    iterations: int
    best_x: float
    best_f: float
    final_temp: float
    accepted: int
    rejected: int
    temperatures: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schedule": self.schedule,
            "iterations": self.iterations,
            "best_x": round(self.best_x, 10),
            "best_f": round(self.best_f, 10),
            "final_temp": round(self.final_temp, 12),
            "accepted": self.accepted,
            "rejected": self.rejected,
            "temp_first": round(self.temperatures[0], 6) if self.temperatures else None,
            "temp_last": round(self.temperatures[-1], 12) if self.temperatures else None,
        }


def golden_cooling(f: Callable[[float], float],
                   x0: float,
                   neighbour: Callable[[float, float], float],
                   t0: float = 1.0,
                   n: int = 200,
                   step: float = 0.1,
                   seed: int = 0,
                   t_min: float = 1e-9) -> CoolingTrace:
    """Simulated annealing with T(k) = T0 * PHI_INV^k."""
    rng = random.Random(seed)
    x = x0
    fx = f(x)
    best_x, best_f = x, fx
    acc = rej = 0
    temps = []
    for k in range(n):
        T = max(t0 * (PHI_INV ** k), t_min)
        temps.append(T)
        x_new = neighbour(x, step)
        f_new = f(x_new)
        delta = f_new - fx
        if delta <= 0 or rng.random() < math.exp(-delta / max(T, 1e-15)):
            x, fx = x_new, f_new
            acc += 1
            if fx < best_f:
                best_x, best_f = x, fx
        else:
            rej += 1
    return CoolingTrace(
        schedule="golden",
        iterations=n, best_x=best_x, best_f=best_f,
        final_temp=temps[-1] if temps else 0.0,
        accepted=acc, rejected=rej, temperatures=temps,
    )


def fibonacci_cooling(f: Callable[[float], float],
                      x0: float,
                      neighbour: Callable[[float, float], float],
                      t0: float = 1.0,
                      n: int = 200,
                      step: float = 0.1,
                      seed: int = 0) -> CoolingTrace:
    """T(k) = T0 / F(k + 2).  Shrinks faster than golden but the
    ratio between temperatures is still φ-ish in the limit."""
    rng = random.Random(seed)
    x = x0
    fx = f(x)
    best_x, best_f = x, fx
    acc = rej = 0
    temps = []
    for k in range(n):
        T = t0 / max(fib(k + 2), 1)
        temps.append(T)
        x_new = neighbour(x, step)
        f_new = f(x_new)
        delta = f_new - fx
        if delta <= 0 or rng.random() < math.exp(-delta / max(T, 1e-15)):
            x, fx = x_new, f_new
            acc += 1
            if fx < best_f:
                best_x, best_f = x, fx
        else:
            rej += 1
    return CoolingTrace(
        schedule="fibonacci",
        iterations=n, best_x=best_x, best_f=best_f,
        final_temp=temps[-1] if temps else 0.0,
        accepted=acc, rejected=rej, temperatures=temps,
    )
