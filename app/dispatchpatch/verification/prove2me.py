from app.dispatchpatch.verification.base import BaseVerification


class Prove2MeVerification(BaseVerification):
    def verify(self, proof: str) -> bool:
        return super().verify(proof) and "proven" in proof.lower()
