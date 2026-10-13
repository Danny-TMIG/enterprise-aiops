
from app.dispatchpatch.orchestration.base import BaseOrchestrator


class OrchestratorRegistry:
    _registry: dict[str, type[BaseOrchestrator]] = {}

    @classmethod
    def register(cls, name: str, orchestrator_cls: type[BaseOrchestrator]):
        cls._registry[name] = orchestrator_cls

    @classmethod
    def get(cls, name: str) -> type[BaseOrchestrator]:
        return cls._registry.get(name, BaseOrchestrator)
