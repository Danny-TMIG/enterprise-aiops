"""Golden section search and Fibonacci search.

Both assume a unimodal function on [a, b]. Both narrow the
interval by a geometric factor. Golden section uses φ; Fibonacci
search uses the Fibonacci numbers directly and is optimal when
the evaluation budget N is known in advance.

Golden section:
    each step, interval shrinks by PHI_INV ≈ 0.618
    N steps -> width * PHI_INV^N

Fibonacci search:
    F(k-1) + F(k-2) = F(k)
    probes at fractions F(k-2)/F(k) and F(k-1)/F(k)
    after k steps, width = width_0 / F(k)
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from app.sacred.constants import PHI_INV, fib


@dataclass
class SearchTrace:
    algorithm: str
    evaluations: int
    x_min: float
    f_min: float
    final_width: float
    history: list[tuple] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "evaluations": self.evaluations,
            "x_min": round(self.x_min, 10),
            "f_min": round(self.f_min, 10),
            "final_width": round(self.final_width, 12),
            "history_len": len(self.history),
        }


def golden_section_search(f: Callable[[float], float],
                          a: float, b: float,
                          tol: float = 1e-9,
                          max_iter: int = 200) -> SearchTrace:
    """Minimise a unimodal function on [a, b] by golden-section.
    Uses only one new evaluation per step (the reused interior
    point is the key efficiency)."""
    if b <= a:
        raise ValueError("need a < b")
    history = []
    # interior points at the golden-section ratio
    invphi = PHI_INV
    x1 = b - invphi * (b - a)
    x2 = a + invphi * (b - a)
    f1, f2 = f(x1), f(x2)
    history.append((a, b, x1, x2, f1, f2))
    evals = 2
    it = 0
    while (b - a) > tol and it < max_iter:
        if f1 < f2:
            b, x2, f2 = x2, x1, f1
            x1 = b - invphi * (b - a)
            f1 = f(x1)
            evals += 1
        else:
            a, x1, f1 = x1, x2, f2
            x2 = a + invphi * (b - a)
            f2 = f(x2)
            evals += 1
        history.append((a, b, x1, x2, f1, f2))
        it += 1
    x_min = (a + b) / 2.0
    return SearchTrace(
        algorithm="golden_section",
        evaluations=evals,
        x_min=x_min,
        f_min=f(x_min),
        final_width=b - a,
        history=history,
    )


def fibonacci_search(f: Callable[[float], float],
                     a: float, b: float,
                     n_evals: int = 20) -> SearchTrace:
    """Minimise a unimodal function on [a, b] using Fibonacci
    probe positions. Optimal for a known evaluation budget N:
    final width = (b - a) / F(N)."""
    if b <= a:
        raise ValueError("need a < b")
    if n_evals < 3:
        raise ValueError("need n_evals >= 3")
    k = n_evals
    history = []
    x1 = a + fib(k - 2) * (b - a) / fib(k)
    x2 = a + fib(k - 1) * (b - a) / fib(k)
    f1, f2 = f(x1), f(x2)
    evals = 2
    while evals < n_evals:
        if f1 < f2:
            b, x2, f2 = x2, x1, f1
            k -= 1
            x1 = a + fib(k - 2) * (b - a) / fib(k)
            f1 = f(x1)
        else:
            a, x1, f1 = x1, x2, f2
            k -= 1
            x2 = a + fib(k - 1) * (b - a) / fib(k)
            f2 = f(x2)
        history.append((a, b, x1, x2, f1, f2))
        evals += 1
    x_min = (a + b) / 2.0
    return SearchTrace(
        algorithm="fibonacci",
        evaluations=evals,
        x_min=x_min,
        f_min=f(x_min),
        final_width=b - a,
        history=history,
    )
