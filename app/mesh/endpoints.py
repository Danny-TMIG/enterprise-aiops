"""Install mesh routes on any FastAPI app (idempotent)."""
from __future__ import annotations

from typing import Any

from fastapi import Body


def install(app) -> None:
    """Add /mesh/status, /mesh/route, /mesh/rebuild to `app` if
    not already present."""
    existing = {getattr(r, "path", None) for r in app.routes}

    if "/mesh/status" not in existing:
        @app.get("/mesh/status")
        def _mesh_status() -> dict[str, Any]:
            from app.mesh.runtime import get_mesh
            m = get_mesh()
            return {"status": "active",
                    "root": getattr(m, "root", ".") or ".",
                    "stats": m.graph.stats()}

    if "/mesh/route" not in existing:
        @app.post("/mesh/route")
        def _mesh_route(payload: dict[str, Any] = Body(default_factory=dict)
                        ) -> dict[str, Any]:
            from app.mesh.router import route as _r
            from app.mesh.runtime import get_mesh
            intent = str(payload.get("intent", ""))
            limit = int(payload.get("limit", 10) or 10)
            m = get_mesh()
            return {"status": "routed", "intent": intent,
                    "matches": _r(intent, m.graph)[:limit]}

    if "/mesh/rebuild" not in existing:
        @app.post("/mesh/rebuild")
        def _mesh_rebuild(payload: dict[str, Any] = Body(default_factory=dict)
                          ) -> dict[str, Any]:
            from app.mesh.runtime import get_mesh
            m = get_mesh()
            return {"status": "rebuilt", "stats": m.graph.stats()}
