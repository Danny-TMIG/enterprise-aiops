from __future__ import annotations

import builtins
from typing import Any

from app.dispatch.verification.base import Prover, ProverResult
from app.dispatch.verification.kernel import Lean4Kernel
from app.dispatch.verification.lean4agent import Lean4Agent
from app.dispatch.verification.leandojo import LeanDojoProver
from app.dispatch.verification.prove2me import Prove2MeProver


class VerificationRegistry:
    def __init__(self) -> None:
        self.provers: dict[str, Prover] = {
            "leandojo":    LeanDojoProver(),
            "prove2me":    Prove2MeProver(),
            "lean4agent":  Lean4Agent(),
            "lean4-kernel": Lean4Kernel(),
        }

    def list(self) -> dict[str, Any]:
        return {n: {"available": p.available()}
                for n, p in self.provers.items()}

    def prove(self, name: str, statement: str,
              context: dict[str, Any] | None = None) -> ProverResult:
        p = self.provers.get(name)
        if not p:
            return ProverResult(prover=name, status="UNSUPPORTED")
        return p.prove(statement, context)

    def verify_all(self, statement: str,
                   evidence: builtins.list[dict[str, Any]] | None = None
                   ) -> builtins.list[ProverResult]:
        ctx = {"evidence": evidence or []}
        return [p.prove(statement, ctx) for p in self.provers.values()]
