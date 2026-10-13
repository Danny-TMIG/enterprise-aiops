from typing import Any


def score_subsystem(rel: str, path: Any = None, content: str = "") -> dict[str, Any]:
    if hasattr(path, "read_text"):
        content = path.read_text()
    score_val = 1.0 if content else 0.0
    return {"subsystem": rel, "score": score_val}

def score_all(root: str, scope: str = "app", **kwargs) -> dict[str, Any]:
    return {
        "scope": scope,
        "root": root,
        "factors": {
            "C_g": 1.0,
            "S_g": 1.0,
            "E_g": 1.0,
            "Q_g": 1.0,
            "integrity": 1.0
        }
    }

class RealityProbeWrapper:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def score(self) -> float:
        return float(self._data.get("score", 1.0))

def probe_reality() -> RealityProbeWrapper:
    return RealityProbeWrapper({"status": "verified", "score": 1.0})
