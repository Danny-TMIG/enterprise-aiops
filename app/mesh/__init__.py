from app.mesh.graph import MeshGraph
from app.mesh.router import route, Node
from app.mesh.runtime import get_mesh

__all__ = ["MeshGraph", "route", "Node", "get_mesh"]


# ── self-registration as capability `mesh` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("mesh")
    def _entry(*args, **kwargs):
        return {"module": "app.mesh", "code": "mesh", "package": True}


_self_register()
