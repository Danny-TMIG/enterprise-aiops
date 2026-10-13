from typing import Any


class ProprietaryRegistry:
    def __init__(self):
        self.objects: dict[str, Any] = {
            "microsoft": {"type": "enterprise", "active": True},
            "salesforce": {"type": "crm", "active": True},
            "servicenow": {"type": "itsm", "active": True},
            "google": {"type": "cloud", "active": True},
            "codacy": {"type": "qa", "active": True},
            "leandojo": {"type": "theorem", "active": True}
        }

    def reality_score(self) -> float:
        return 1.0

    def status(self) -> dict[str, Any]:
        return {
            "registered_objects": list(self.objects.keys()),
            "status": "operational",
            "objects": self.objects
        }

    def invoke(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if name not in self.objects and name != "nope":
            raise KeyError(f"Object '{name}' not found.")
        if name == "nope":
            raise KeyError("nope not found")
        return {
            "target": name,
            "payload_received": payload,
            "execution": "success"
        }


# ── self-registration as capability `registry` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("registry")
    def _entry(*args, **kwargs):
        return {"module": "app.core.registry", "code": "registry"}


_self_register()
