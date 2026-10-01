from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.dispatch.verification.base import Prover, ProverResult
from app.dispatch.verification.leandojo import LeanDojoProver
from app.dispatch.verification.prove2me import Prove2MeProver
from app.dispatch.verification.lean4agent import Lean4Agent
from app.dispatch.verification.kernel import Lean4Kernel


class VerificationRegistry:
    def __init__(self) -> None:
        self.provers: Dict[str, Prover] = {
            "leandojo":    LeanDojoProver(),
            "prove2me":    Prove2MeProver(),
            "lean4agent":  Lean4Agent(),
            "lean4-kernel": Lean4Kernel(),
        }

    def list(self) -> Dict[str, Any]:
        return {n: {"available": p.available()}
                for n, p in self.provers.items()}

    def prove(self, name: str, statement: str,
              context: Optional[Dict[str, Any]] = None) -> ProverResult:
        p = self.provers.get(name)
        if not p:
            return ProverResult(prover=name, status="UNSUPPORTED")
        return p.prove(statement, context)

    def verify_all(self, statement: str,
                   evidence: Optional[List[Dict[str, Any]]] = None
                   ) -> List[ProverResult]:
        ctx = {"evidence": evidence or []}
        return [p.prove(statement, ctx) for p in self.provers.values()]
