"""Backwards-compat shim.

The canonical implementation is app.mesh. This module exists
so that any code still doing `import mesh` keeps working.
"""
from app.mesh import *
from app.mesh import (  # noqa: F401
    PLANES,
    RESULT_STATES,
    ROUTING_DIMENSIONS,
    SKILL_FAMILIES,
    Edge,
    MeshGraph,
    MeshRuntime,
    Node,
    get_mesh,
    route,
)

try:
    from app.mesh.convergence import (  # noqa: F401
        ConvergenceMetrics,
        MeshConvergenceValidator,
    )
except Exception:
    pass
