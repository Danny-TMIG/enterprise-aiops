from typing import Dict, Type
from app.dispatchpatch.verification.base import BaseVerification

class VerificationRegistry:
    _registry: Dict[str, Type[BaseVerification]] = {}

    @classmethod
    def register(cls, name: str, verifier_cls: Type[BaseVerification]):
        cls._registry[name] = verifier_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseVerification]:
        return cls._registry.get(name, BaseVerification)
