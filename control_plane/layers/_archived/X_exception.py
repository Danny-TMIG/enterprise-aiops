"""X — eXception. Role: Handle."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from control_plane.layer_base import LayerBase


@dataclass
class eXceptionLayer(LayerBase):
    letter: str = "X"
    name: str = "eXception"
    role: str = "Handle"
    reads: tuple[str, ...] = ("ANY_REJECTION",)
    writes: tuple[str, ...] = ("ExceptionRecord",)
    pollinates: tuple[str, ...] = ("M", "Z")
    artifact: str = "exception-record"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        rejections = inputs.get("ANY_REJECTION") or {}
        if not isinstance(rejections, dict) or not rejections:
            return {
                "artifact": self.artifact,
                "produced_by": f"{self.letter}.{self.name}",
                "reads": ["ANY_REJECTION"],
                "summary": "No exception on this run.",
                "origin_layer": "none",
                "failure_class": "none",
                "recovery": "terminate",
            }
        origin = next(iter(rejections))
        detail = rejections[origin]
        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["ANY_REJECTION"],
            "summary": f"Exception from {origin}.",
            "origin_layer": str(origin),
            "failure_class": str(detail.get("status", "EXECUTION_FAILURE")) if isinstance(detail, dict) else "EXECUTION_FAILURE",
            "recovery": "escalate",
        }
