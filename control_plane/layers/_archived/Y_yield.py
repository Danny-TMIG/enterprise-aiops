"""Y — Yield. Role: Realize."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from control_plane.layer_base import LayerBase


@dataclass
class YieldLayer(LayerBase):
    letter: str = "Y"
    name: str = "Yield"
    role: str = "Realize"
    reads: tuple[str, ...] = ("Q", "V")
    writes: tuple[str, ...] = ("YieldReport",)
    pollinates: tuple[str, ...] = ("Z",)
    artifact: str = "yield-report"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        quality = inputs.get("Q") or {}
        variance = inputs.get("V") or {}
        total = len(quality.get("criteria", []))
        passed = sum(1 for c in quality.get("criteria", []) if c.get("passed"))
        quality_yield = (passed / total) if total else 0.0
        variances = variance.get("variances", [])
        cost_yield = 1.0
        if variances:
            pct = float(variances[0].get("pct", 0.0))
            cost_yield = max(0.0, 1.0 - abs(pct) / 100.0)
        composite = (quality_yield + cost_yield) / 2.0
        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["Q", "V"],
            "summary": f"Yield quality {quality_yield:.2f} cost {cost_yield:.2f} composite {composite:.2f}.",
            "quality_yield": quality_yield,
            "cost_yield": cost_yield,
            "composite_yield": composite,
        }
