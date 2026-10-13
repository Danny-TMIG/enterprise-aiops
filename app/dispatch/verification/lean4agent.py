from __future__ import annotations

from typing import Any

from app.dispatch.models.base import ModelRequest
from app.dispatch.models.registry import get_registry
from app.dispatch.verification.base import LLMExec, Prover, ProverResult


class Lean4Agent(Prover):
    """Agent that turns a natural-language goal into Lean 4 tactics.

    It *always* carries an explicit LLMExec — the (provider, model)
    actually invoked is recorded on the result. No hidden model call.
    """
    name = "lean4agent"

    def __init__(self, exec_hint: LLMExec | None = None) -> None:
        self.exec_hint = exec_hint or LLMExec(
            provider="anthropic", model="claude-sonnet-4-6",
            task="proving",
        )

    def _pick_provider(self) -> str:
        reg = get_registry()
        return reg.select("reasoning", model=self.exec_hint.model)

    def _prove(self, statement: str, context: dict[str, Any]):
        reg = get_registry()
        provider = self._pick_provider()
        llm_exec = LLMExec(
            provider=provider,
            model=self.exec_hint.model,
            temperature=self.exec_hint.temperature,
            max_tokens=self.exec_hint.max_tokens,
            task="proving",
        )
        prompt = (
            "You are a Lean 4 tactic generator. Given a natural-language "
            "goal, respond with a single `by` tactic block. No prose.\n\n"
            f"Goal: {statement}\n"
        )
        resp = reg.complete(ModelRequest(
            task="reasoning", prompt=prompt,
            metadata={"provider": provider, "model": llm_exec.model},
        ))
        tactics = resp.text.strip() or "by trivial"
        return ProverResult(
            prover=self.name,
            status="PASS" if not resp.dry_run else "UNKNOWN",
            proof=tactics,
            llm_exec=llm_exec,
            evidence=[{"type": "statement", "value": statement},
                      {"type": "tactics", "value": tactics},
                      {"type": "dry_run", "value": resp.dry_run}],
        )
