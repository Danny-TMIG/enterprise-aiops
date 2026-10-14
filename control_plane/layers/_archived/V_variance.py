"""V — Variance. Role: Compare."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from control_plane.layer_base import LayerBase


@dataclass
class VarianceLayer(LayerBase):
    letter: str = "V"
    name: str = "Variance"
    role: str = "Compare"
    reads: tuple[str, ...] = ("C", "U")
    writes: tuple[str, ...] = ("VarianceReport",)
    pollinates: tuple[str, ...] = ("E", "Y")
    artifact: str = "variance-report"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        norm = inputs.get("C") or {}
        usage = inputs.get("U") or {}
        total_actual = 0.0
        for a in usage.get("attributions", []):
            if a.get("unit") == "cost_usd":
                total_actual += float(a.get("quantity", 0.0))
        expected = float(norm.get("median", 0.0))
        delta = total_actual - expected
        pct = (delta / expected * 100.0) if expected else 0.0
        flag = "material" if abs(pct) > 200 else "notable" if abs(pct) > 100 else "within-norm"
        variances = [
            {
                "dimension": "cost_usd",
                "expected": expected,
                "actual": total_actual,
                "delta": delta,
                "pct": pct,
                "flag": flag,
            }
        ]
        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["C", "U"],
            "summary": f"Variance {delta:.2f} ({pct:.1f}%) flag {flag}.",
            "variances": variances,
        }
