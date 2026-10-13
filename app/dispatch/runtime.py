from typing import Any


class ModelRegistry:
    def __init__(self):
        self.registry: dict[str, dict[str, Any]] = {}

    def register(self, name: str, config: dict[str, Any]) -> None:
        self.registry[name] = config

    def status(self) -> dict[str, Any]:
        return {
            "total_models": len(self.registry),
            "models": list(self.registry.keys()),
            "registry_state": "active"
        }

class DummyProvider:
    def list(self) -> list[str]:
        return ["provider-1"]

class DisRuntime:
    def __init__(self, models: ModelRegistry = None):
        self.models = models or ModelRegistry()
        self.orchestration = DummyProvider()
        self.verification = DummyProvider()
        self.scan = DummyProvider()
        self.evidence = DummyProvider()
        self.mcp = type("MCP", (), {"tools": {"default": {}}})()
        self.a2a = type("A2A", (), {"card": type("Card", (), {"skills": [{"id": "skill-1"}]})()})()

    def status(self) -> dict[str, Any]:
        return {
            "runtime": "DIS",
            "models": self.models.status(),
            "orchestration": self.orchestration.list(),
            "verification": self.verification.list(),
            "scan": self.scan.list(),
            "evidence": self.evidence.list(),
            "protocols": {
                "mcp": {"tools": list(self.mcp.tools.keys())},
                "a2a": {"skills": [s["id"] for s in self.a2a.card.skills]},
            },
        }

def get_dis() -> DisRuntime:
    return DisRuntime()
