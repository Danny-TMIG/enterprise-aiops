from app.dispatchpatch.verification.base import BaseVerification


class LeanDojoVerification(BaseVerification):
    def verify(self, proof: str) -> bool:
        return super().verify(proof) and "dojo" in proof.lower()
