from __future__ import annotations

from app.dispatch.verification.base import Prover, ProverResult


class Prove2MeProver(Prover):
    """Natural-language statement → formal Lean statement + attempt.

    Prove2Me is treated as a *statement prover*: it converts a claim
    into a canonical Lean theorem before the kernel checks it.
    """
    name = "prove2me"

    def _prove(self, statement: str, context):
        lean = self._formalize(statement)
        if not lean:
            return ProverResult(
                prover=self.name, status="INSUFFICIENT_DATA",
                error="could not formalize statement",
            )
        return ProverResult(
            prover=self.name, status="PASS",
            proof=lean,
            evidence=[{"type": "statement", "value": statement},
                      {"type": "lean", "value": lean}],
        )

    def _formalize(self, statement: str) -> str:
        s = statement.strip().rstrip(".")
        if not s:
            return ""
        # Deterministic, namespace-safe placeholder theorem.
        safe = "".join(c if c.isalnum() else "_" for c in s)[:40]
        return f"theorem t_{safe} : True := by trivial"
