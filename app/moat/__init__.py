from app.moat.axes import Axis, AxisScore, AXES, score_subsystem, score_all
from app.moat.moat import MoatMesh, MoatEquation, record_run

__all__ = [
    "Axis", "AxisScore", "AXES", "score_subsystem", "score_all",
    "MoatMesh", "MoatEquation", "record_run",
]


# ── self-registration as capability `moat` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("moat")
    def _entry(*args, **kwargs):
        return {"module": "app.moat", "code": "moat", "package": True}


_self_register()
