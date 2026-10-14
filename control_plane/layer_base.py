"""Shared base class for all A-Z layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from control_plane.executor import Executor


@dataclass
class LayerResult:
    letter: str
    artifact: str
    status: str
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerBase:
    """Every layer reads declared inputs and produces one artifact.

    A layer must implement _produce. If it does not, execute returns
    EXECUTION_FAILURE. There is no default payload.
    """

    letter: str = "?"
    name: str = "Base"
    role: str = "base"
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    pollinates: tuple[str, ...] = ()
    artifact: str = "unknown"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Layer-specific derivation. Must be overridden by every layer."""
        raise NotImplementedError(f"layer {self.letter} does not implement _produce")

    def execute(self, context: dict[str, Any]) -> LayerResult:
        inputs: dict[str, Any] = {}
        for key in self.reads:
            if key in ("input", "ALL", "ANY_REJECTION"):
                inputs[key] = context.get(key, {})
            else:
                inputs[key] = context.get(key)

        missing = [k for k in self.reads
                   if k not in ("input", "ALL", "ANY_REJECTION")
                   and inputs.get(k) is None]
        if missing:
            return LayerResult(
                letter=self.letter,
                artifact=self.artifact,
                status="BLOCKED",
                reason=f"missing required inputs: {missing}",
                payload={},
            )

        executor = Executor.from_env()
        payload, error = executor.execute(
            self.letter, self.name, self.artifact,
            inputs, context, produce=self._produce,
        )
        if error:
            return LayerResult(
                letter=self.letter,
                artifact=self.artifact,
                status="EXECUTION_FAILURE",
                reason=error,
                payload=payload,
            )
        return LayerResult(
            letter=self.letter,
            artifact=self.artifact,
            status="PASS",
            reason="",
            payload=payload,
        )
