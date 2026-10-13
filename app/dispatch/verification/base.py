from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class LLMExec:
    """Explicit, auditable pointer to the model used by an agent.

    Lean4Agent *always* carries one of these — no hidden model calls.
    """
    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 2048
    task: str = "proving"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider, "model": self.model,
            "temperature": self.temperature, "max_tokens": self.max_tokens,
            "task": self.task,
        }


@dataclass
class ProverResult:
    prover: str
    status: str
    proof: str | None = None
    error: str | None = None
    elapsed_ms: int = 0
    llm_exec: LLMExec | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    ts: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "prover": self.prover, "status": self.status,
            "proof": self.proof, "error": self.error,
            "elapsed_ms": self.elapsed_ms,
            "evidence": self.evidence, "ts": self.ts,
        }
        if self.llm_exec:
            d["llm_exec"] = self.llm_exec.to_dict()
        return d


class Prover:
    name = "prover"

    def available(self) -> bool:
        return True

    def prove(self, statement: str,
              context: dict[str, Any] | None = None) -> ProverResult:
        import time
        ctx = context or {}
        t0 = time.time()
        try:
            r = self._prove(statement, ctx)
        except Exception as exc:  # noqa: BLE001
            r = ProverResult(prover=self.name, status="EXECUTION_FAILURE",
                             error=type(exc).__name__)
        r.elapsed_ms = int((time.time() - t0) * 1000)
        return r

    def _prove(self, statement: str,
               context: dict[str, Any]) -> ProverResult:  # pragma: no cover
        raise NotImplementedError
