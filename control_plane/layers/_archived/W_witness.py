"""W — Witness. Role: Corroborate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from control_plane.layer_base import LayerBase


@dataclass
class WitnessLayer(LayerBase):
    letter: str = "W"
    name: str = "Witness"
    role: str = "Corroborate"
    reads: tuple[str, ...] = ("E", "T", "P")
    writes: tuple[str, ...] = ("WitnessVerdict",)
    pollinates: tuple[str, ...] = ("Z",)
    artifact: str = "witness-verdict"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        receipt = inputs.get("E") or {}
        trust = inputs.get("T") or {}
        provenance = inputs.get("P") or {}
        baseline = float(receipt.get("baseline_usd", 0.0))
        actual = float(receipt.get("actual_usd", 0.0))
        reported = float(receipt.get("delta_usd", 0.0))
        recomputed = baseline - actual
        tol = 1e-9
        if abs(recomputed - reported) > tol:
            verdict = "disputed"
            reason = f"reported {reported} recomputed {recomputed}"
        elif not provenance.get("chain_head"):
            verdict = "not-recomputable"
            reason = "provenance chain empty"
        elif not trust.get("artifact_root"):
            verdict = "not-recomputable"
            reason = "attestation root empty"
        else:
            verdict = "confirmed"
            reason = f"recomputed {recomputed}"
        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["E", "T", "P"],
            "summary": f"Witness {verdict}: {reason}.",
            "verdict": verdict,
            "receipt_hash": str(trust.get("artifact_root", "")),
        }
