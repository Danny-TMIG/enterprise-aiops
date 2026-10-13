from collections.abc import Callable
from typing import Any


class ProprietaryRegistry:
    def __init__(self):
        self.objects: dict[str, Callable] = {
            "microsoft": lambda *a, **kw: "microsoft-ok",
            "salesforce": lambda *a, **kw: "salesforce-ok",
            "servicenow": lambda *a, **kw: "servicenow-ok",
            "google": lambda *a, **kw: "google-ok",
            "codacy": lambda *a, **kw: "codacy-ok",
            "leandojo": lambda *a, **kw: "leandojo-ok",
        }

    def status(self) -> dict[str, Any]:
        return {"registry": "proprietary", "objects": list(self.objects.keys())}

    def reality_score(self) -> float:
        return 1.0

    def invoke(self, name: str, *args, **kwargs) -> Any:
        if name not in self.objects:
            raise KeyError(f"Object {name} not found in proprietary registry.")
        return self.objects[name](*args, **kwargs)
