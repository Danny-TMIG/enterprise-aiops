"""Multiple comparison control."""
from __future__ import annotations

from typing import Any


def bonferroni(alpha: float, m: int) -> dict[str, Any]:
    if m <= 0:
        return {"available": True, "alpha_prime": alpha, "m": 0}
    return {"available": True, "alpha_prime": round(alpha / m, 8), "m": m}


def benjamini_hochberg(p_values: list[float],
                       alpha: float = 0.05) -> dict[str, Any]:
    m = len(p_values)
    if m == 0:
        return {"available": True, "rejected": [], "m": 0, "k_max": 0}
    order = sorted(range(m), key=lambda i: p_values[i])
    k_max = 0
    for k in range(1, m + 1):
        if p_values[order[k - 1]] <= (k / m) * alpha:
            k_max = k
    rejected = [order[i] for i in range(k_max)]
    return {
        "available": True,
        "m": m,
        "k_max": k_max,
        "rejected": rejected,
        "threshold": round((k_max / m) * alpha, 8) if k_max else 0.0,
    }
