from typing import Any


class ModelRegistry:
    def __init__(self):
        self._models: dict[str, Any] = {}

    def status(self) -> dict[str, Any]:
        return {
            "models": list(self._models.keys()),
            "count": len(self._models),
            "state": "operational"
        }
