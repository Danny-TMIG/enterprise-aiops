from app.dispatchpatch.verification.base import BaseVerification


class Lean4AgentVerification(BaseVerification):
    def verify(self, proof: str) -> bool:
        return super().verify(proof) and "lean" in proof.lower()
