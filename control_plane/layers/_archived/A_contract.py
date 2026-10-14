"""A — Contract. Role: Define."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from control_plane.layer_base import LayerBase, LayerResult


@dataclass
class ContractLayer(LayerBase):
    """A: Contract. Defines the execution-contract."""

    letter: str = "A"
    name: str = "Contract"
    role: str = "Define"
    reads: tuple[str, ...] = ("input",)
    writes: tuple[str, ...] = ("ExecutionContract",)
    pollinates: tuple[str, ...] = ("L", "G", "F")
    artifact: str = "execution-contract"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Real derivation. Reads the request, returns the schema-shaped contract.

        The prompt in prompts/A-contract.md describes the same derivation.
        When ASF_EXECUTOR=llm, this method is bypassed and the executor
        sends the prompt to a model instead.
        """
        request = inputs.get("input") or {}
        if not isinstance(request, dict):
            request = {}

        def field(name: str, fallback: Any) -> Any:
            v = request.get(name)
            return v if v is not None else fallback

        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["input"],
            "summary": "Derived execution contract from work request.",
            "unit": str(field("unit", "unknown")),
            "quantity": int(field("quantity", 1)),
            "quality_floor": str(field("quality_bar", "unstated")),
            "deadline": str(field("deadline", "unknown")),
            "risk_class": str(field("risk_class", "R3")),
            "budget_ceiling_usd": float(field("budget_ceiling_usd", 0.0)),
            "oversight_requirement": str(field("oversight_requirement", "none")),
        }
