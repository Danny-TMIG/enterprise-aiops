from app.botnetmastery.models import Bot, Task
from app.botnetmastery.c2 import C2Server
from app.botnetmastery.simulation import Simulation

__all__ = ["Bot", "Task", "C2Server", "Simulation"]


# ── self-registration as capability `botnetmastery` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("botnetmastery")
    def _entry(*args, **kwargs):
        return {"module": "app.botnetmastery", "code": "botnetmastery", "package": True}


_self_register()
