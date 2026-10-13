
from app.dispatchpatch.evidence.base import DispatchEvidence


class EvidenceRegistry:
    _registry: dict[str, type[DispatchEvidence]] = {}

    @classmethod
    def register(cls, name: str, evidence_cls: type[DispatchEvidence]):
        cls._registry[name] = evidence_cls

    @classmethod
    def get(cls, name: str) -> type[DispatchEvidence]:
        return cls._registry.get(name, DispatchEvidence)
