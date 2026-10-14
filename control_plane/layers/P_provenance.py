"""P — Provenance. Role: Trace."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from control_plane.layer_base import LayerBase, LayerResult


@dataclass
class ProvenanceLayer(LayerBase):
    """P: Provenance. Traces the provenance-chain."""

    letter: str = "P"
    name: str = "Provenance"
    role: str = "Trace"
    reads: tuple[str, ...] = ('ALL',)
    writes: tuple[str, ...] = ('ProvenanceChain',)
    pollinates: tuple[str, ...] = ('T', 'W')
    artifact: str = "provenance-chain"

    def execute(self, context: dict[str, Any]) -> LayerResult:
        """Read declared inputs, produce the artifact, record evidence."""
        inputs = {}
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

        payload = self._produce(inputs, context)
        return LayerResult(
            letter=self.letter,
            artifact=self.artifact,
            status="PASS",
            reason="",
            payload=payload,
        )

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Placeholder artifact. Real layer logic substitutes here."""
        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": sorted(k for k in inputs),
            "summary": f"{self.name} produced {self.artifact}",
        }
