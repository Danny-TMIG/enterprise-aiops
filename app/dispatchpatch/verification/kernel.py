from app.dispatchpatch.verification.base import BaseVerification


class KernelVerification(BaseVerification):
    def verify(self, proof: str) -> bool:
        return super().verify(proof) and len(proof) > 0
