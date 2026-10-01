from typing import Dict, Type
from app.dispatchpatch.orchestration.base import BaseOrchestrator

class OrchestratorRegistry:
    _registry: Dict[str, Type[BaseOrchestrator]] = {}

    @classmethod
    def register(cls, name: str, orchestrator_cls: Type[BaseOrchestrator]):
        cls._registry[name] = orchestrator_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseOrchestrator]:
        return cls._registry.get(name, BaseOrchestrator)
