from typing import Dict, Any

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, Any] = {}

    def status(self) -> Dict[str, Any]:
        return {
            "models": list(self._models.keys()),
            "count": len(self._models),
            "state": "operational"
        }
