"""SOM neighborhood update."""
from __future__ import annotations

import math
from typing import Any


def neighborhood(d_c: float, d_i: float, sigma: float) -> float:
    return math.exp(-((d_c - d_i) ** 2) / (2 * max(sigma, 1e-9) ** 2))


def som_update(positions: list[float], target: float,
               learning_rate: float = 0.1,
               sigma: float = 1.0) -> dict[str, Any]:
    if not positions:
        return {"available": True, "updated": []}
    c = min(range(len(positions)), key=lambda i: abs(positions[i] - target))
    updated = []
    for i, w in enumerate(positions):
        h = neighborhood(float(c), float(i), sigma)
        updated.append(round(w + learning_rate * h * (target - w), 6))
    return {"available": True, "c": c, "updated": updated}
