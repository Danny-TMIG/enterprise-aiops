from typing import Dict, Type
from app.dispatchpatch.evidence.base import DispatchEvidence

class EvidenceRegistry:
    _registry: Dict[str, Type[DispatchEvidence]] = {}

    @classmethod
    def register(cls, name: str, evidence_cls: Type[DispatchEvidence]):
        cls._registry[name] = evidence_cls

    @classmethod
    def get(cls, name: str) -> Type[DispatchEvidence]:
        return cls._registry.get(name, DispatchEvidence)
