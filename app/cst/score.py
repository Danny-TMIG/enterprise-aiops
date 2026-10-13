"""Score = sum over completed loops of nontriviality · reversibility."""
from __future__ import annotations

from typing import Any


def k(loops: list[dict[str, Any]]) -> dict[str, Any]:
    complete = [l for l in loops if l.get("status") == "complete"]
    if not complete:
        return {"k": 0.0, "loops": 0, "mean_nontriviality": 0.0,
                "reversibility": 0.0, "status": "no-complete-loops"}

    score = sum(l["nontriviality"] * l["reversibility"] for l in complete)
    mean_nt = sum(l["nontriviality"] for l in complete) / len(complete)
    mean_rev = sum(l["reversibility"] for l in complete) / len(complete)

    return {
        "k": round(score, 4),
        "loops": len(complete),
        "mean_nontriviality": round(mean_nt, 4),
        "reversibility": round(mean_rev, 4),
        "status": "complete" if mean_rev == 1.0 else "drift",
    }


def report(loops: list[dict[str, Any]]) -> str:
    s = k(loops)
    lines = [
        "── Constructive Self-Transcendence ──",
        f"  k                   {s['k']}",
        f"  completed loops     {s['loops']}",
        f"  mean nontriviality  {s['mean_nontriviality']}",
        f"  reversibility       {s['reversibility']}",
        f"  status              {s['status']}",
    ]
    return "\n".join(lines)
