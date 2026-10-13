"""get_mesh() + install_routes(app)."""
from __future__ import annotations

from app.mesh.graph import MeshGraph


def get_mesh() -> MeshGraph:
    return MeshGraph()


def install_routes(app) -> None:
    @app.get("/mesh/status")
    def _status():
        g = get_mesh()
        return {"root": ".", "stats": g.stats()}

    @app.post("/mesh/route")
    def _route():
        return {"status": "routed"}

    @app.post("/mesh/rebuild")
    def _rebuild():
        return {"status": "rebuilt"}
