"""Sacred-geometry mathematics that is actually load-bearing.

Four constants and three algorithms survive the audit:

    PHI          golden ratio      1.618033988...
    PHI_INV      inverse golden    0.618033988...
    FIB          Fibonacci numbers 0,1,1,2,3,5,8,13,...
    PLATONIC     dodecahedron/icosahedron vertex counts

    golden_section_search   narrows an interval by φ each step
    fibonacci_search        optimal for known evaluation budget N
    golden_cooling          φ-based annealing schedule

Nothing about crystals, vibrations, or pyramid energy. Only
what has a proof.
"""
from app.sacred.constants import (
    PHI, PHI_INV, PHI_SQ, SILVER_RATIO,
    fib, fib_seq, fib_ge, FIBONACCI,
)
from app.sacred.search import (
    golden_section_search, fibonacci_search,
    SearchTrace,
)
from app.sacred.cooling import (
    golden_cooling, fibonacci_cooling, CoolingTrace,
)
from app.sacred.alloc import (
    fib_alloc, phi_ewma_alpha, golden_ratio_tick, golden_tick_2d,
)
from app.sacred.geometry import (
    platonic_counts, dodeca_vertices, icosa_vertices,
    golden_angle, phyllotaxis,
)

__all__ = [
    "PHI", "PHI_INV", "PHI_SQ", "SILVER_RATIO",
    "fib", "fib_seq", "fib_ge", "FIBONACCI",
    "golden_section_search", "fibonacci_search", "SearchTrace",
    "golden_cooling", "fibonacci_cooling", "CoolingTrace",
    "fib_alloc", "phi_ewma_alpha", "golden_ratio_tick",
    "golden_tick_2d",
    "platonic_counts", "dodeca_vertices", "icosa_vertices",
    "golden_angle", "phyllotaxis",
]
