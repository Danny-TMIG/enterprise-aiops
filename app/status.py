"""Unified status for every layer. Never raises."""
from __future__ import annotations

from typing import Any


def _safe(fn) -> Any:
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        return {"error": type(exc).__name__}


def unified_status() -> dict[str, Any]:
    out: dict[str, Any] = {"layers": {}}

    def mesh():
        from app.mesh.runtime import get_mesh
        return get_mesh().status()

    def dis():
        from app.dispatch.runtime import get_dis
        return get_dis().status()

    def autonomy():
        from app.autonomy.runtime import get_runtime
        rt = get_runtime()
        return {"rules": rt.engine.rules(),
                "remedies": rt.healer.available()}

    def seed():
        from app.seed.runtime import get_seed
        return get_seed().status()

    def topos():
        from app.topos.runtime import get_topos
        return get_topos().status()

    def botnet():
        from app.botnetmastery.c2 import C2Server  # noqa: F401
        return {"available": True}

    out["layers"]["mesh"] = _safe(mesh)
    out["layers"]["dis"] = _safe(dis)
    out["layers"]["autonomy"] = _safe(autonomy)
    out["layers"]["seed"] = _safe(seed)
    out["layers"]["topos"] = _safe(topos)
    out["layers"]["botnetmastery"] = _safe(botnet)

    out["ok"] = all(
        isinstance(v, dict) and "error" not in v
        for v in out["layers"].values()
    )
    return out
