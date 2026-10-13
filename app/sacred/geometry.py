"""Sacred-geometry counts that are provably correct.

The dodecahedron has 12 faces, 20 vertices, 30 edges. The
icosahedron has 20 faces, 12 vertices, 30 edges. Both embed the
golden ratio in their coordinates. These are exact integer facts,
not mysticism.

The golden angle 2π(1 - 1/φ) ≈ 137.5° is the angle between
successive leaves (or seeds) in the phyllotaxis pattern.
"""
from __future__ import annotations

import math

from app.sacred.constants import PHI_INV


def dodeca_vertices() -> int:
    return 20


def icosa_vertices() -> int:
    return 12


def platonic_counts() -> dict[str, dict[str, int]]:
    """Faces / vertices / edges of the five Platonic solids."""
    return {
        "tetrahedron": {"faces": 4,  "vertices": 4,  "edges": 6},
        "cube":        {"faces": 6,  "vertices": 8,  "edges": 12},
        "octahedron":  {"faces": 8,  "vertices": 6,  "edges": 12},
        "dodecahedron":{"faces": 12, "vertices": 20, "edges": 30},
        "icosahedron": {"faces": 20, "vertices": 12, "edges": 30},
    }


def golden_angle() -> float:
    """2π (1 - 1/φ) in radians ≈ 2.39996."""
    return 2.0 * math.pi * (1.0 - PHI_INV)


def phyllotaxis(n: int, r_max: float = 1.0):
    """Generator of n points on a disk with the golden-angle
    radial construction — the same math that gives sunflower
    seed packing.  Yields (x, y)."""
    ga = golden_angle()
    for k in range(1, n + 1):
        r = r_max * math.sqrt(k / n)
        theta = k * ga
        yield (r * math.cos(theta), r * math.sin(theta))
