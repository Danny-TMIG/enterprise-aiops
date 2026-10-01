"""Backwards-compat shim.

The canonical implementation is app.mesh. This module exists
so that any code still doing `import mesh` keeps working.
"""
from app.mesh import *  # noqa: F401,F403
from app.mesh import (  # noqa: F401
    MeshGraph, Node, Edge,
    route,
    MeshRuntime, get_mesh,
    PLANES, SKILL_FAMILIES, RESULT_STATES, ROUTING_DIMENSIONS,
)
try:
    from app.mesh.convergence import (  # noqa: F401
        MeshConvergenceValidator, ConvergenceMetrics,
    )
except Exception:
    pass
