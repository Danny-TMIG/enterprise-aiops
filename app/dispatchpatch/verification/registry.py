
from app.dispatchpatch.verification.base import BaseVerification


class VerificationRegistry:
    _registry: dict[str, type[BaseVerification]] = {}

    @classmethod
    def register(cls, name: str, verifier_cls: type[BaseVerification]):
        cls._registry[name] = verifier_cls

    @classmethod
    def get(cls, name: str) -> type[BaseVerification]:
        return cls._registry.get(name, BaseVerification)
