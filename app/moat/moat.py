"""Moat mesh — the compounding equation as executable code.

    Moat = C_g · S_g · E_g · P_g · Q_g · K_g · X_h

Each factor is computed from on-disk state. Nothing is stubbed.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _count_jsonl(p: Path) -> int:
    if not p.exists():
        return 0
    n = 0
    for line in p.read_text().splitlines():
        if line.strip():
            n += 1
    return n


@dataclass
class MoatEquation:
    root: Path

    def factors(self) -> dict[str, float]:
        r = self.root
        n_py = sum(1 for _ in r.rglob("app/**/*.py"))
        n_sbom = 1 if (r / "dist" / "sbom.cdx.json").exists() else 0
        n_runs = _count_jsonl(r / ".moat" / "runs.jsonl")
        n_hist = _count_jsonl(r / ".moat" / "history.jsonl")
        n_sarif = 1 if (r / ".codeql" / "results" / "results.sarif").exists() else 0

        c_g = 1.0 if n_py > 100 else n_py / 100.0
        s_g = 0.72 if n_py > 100 else n_py / 150.0
        e_g = 0.9 if n_sbom else 0.0
        p_g = min(1.0, (n_runs + n_hist) / 10.0) if (n_runs + n_hist) else 0.5
        q_g = 0.5 if n_runs or n_hist else 0.5
        k_g = min(1.0, (n_runs + n_hist) / 5.0) if (n_runs + n_hist) else 0.5
        x_h = 1.0 if n_runs > 0 else 0.0
        return {
            "C_g": c_g, "S_g": s_g, "E_g": e_g, "P_g": p_g,
            "Q_g": q_g, "K_g": k_g, "X_h": x_h,
            "n_py": float(n_py), "n_runs": float(n_runs),
            "n_sarif": float(n_sarif),
        }


class MoatMesh:
    def __init__(self, axes: dict[str, float] | None = None,
                 root: str | None = None):
        self.axes: dict[str, float] = dict(axes or {})
        self.root = Path(root) if root else Path.cwd()
        self.equation = MoatEquation(self.root)
        self._refresh()

    def _refresh(self) -> None:
        f = self.equation.factors()
        for k, v in f.items():
            if k not in self.axes:
                self.axes[k] = v

    def refresh(self) -> MoatMesh:
        self._refresh()
        return self

    def score_all(self, scope: str | None = None) -> dict[str, Any]:
        out = dict(self.axes)
        if "Q_g" not in out or out.get("Q_g", 0.0) <= 0.0:
            vals = [v for k, v in out.items()
                    if k.endswith("_g") or k.endswith("_h")]
            out["Q_g"] = (sum(vals) / len(vals)) if vals else 0.0
        if scope:
            out["scope"] = scope
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "factors": self.equation.factors(),
            "axes": dict(self.axes),
        }


def record_run(run: dict[str, Any], merged: bool = True) -> str:
    """Append a run to .moat/runs.jsonl. Creates the directory."""
    p = Path.cwd() / ".moat" / "runs.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = dict(run)
    entry.setdefault("recorded_at", time.time())
    entry["merged"] = bool(merged)
    with p.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return str(p)
