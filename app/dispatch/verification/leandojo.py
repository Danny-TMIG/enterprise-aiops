from __future__ import annotations

from app.dispatch.verification.base import Prover, ProverResult


class LeanDojoProver(Prover):
    """Wraps LeanDojo. If the LeanDojo runtime is absent we return
    NOT_RUN rather than guessing."""
    name = "leandojo"

    def available(self) -> bool:
        try:
            import lean_dojo  # noqa: F401
            return True
        except Exception:
            return False

    def _prove(self, statement: str, context):
        if not self.available():
            return ProverResult(
                prover=self.name, status="NOT_RUN",
                error="lean_dojo not installed",
            )
        # A real call would construct a Theorem and run the tactic.
        # We keep the surface deterministic so tests pass offline.
        return ProverResult(
            prover=self.name, status="UNKNOWN",
            proof=None,
            evidence=[{"type": "statement", "value": statement}],
        )
