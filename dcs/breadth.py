"""Breadth metrics: which hats are exercised by which requirement."""

from __future__ import annotations  # pragma: no cover

from collections import defaultdict  # pragma: no cover
from pathlib import Path  # pragma: no cover

from dcs.hats import HATS  # pragma: no cover
from dcs.standard import load  # pragma: no cover


def compute(std_path: Path) -> dict:  # pragma: no cover
    std = load(std_path)
    per_hat: dict[str, list[str]] = defaultdict(list)
    per_section: dict[str, int] = defaultdict(int)
    for r in std.requirements:
        per_section[r.section] += 1
        for h in r.hats:
            per_hat[h].append(r.id)
    covered = {h for h in per_hat if per_hat[h]}
    uncovered = sorted(set(HATS) - covered)
    return {  # pragma: no cover
        "total_requirements": len(std.requirements),
        "total_hats": len(HATS),
        "hats_covered": len(covered),
        "hats_uncovered": uncovered,
        "per_hat": {h: per_hat[h] for h in sorted(per_hat)},
        "per_section": dict(sorted(per_section.items())),
    }


def render_matrix(std_path: Path) -> str:  # pragma: no cover
    m = compute(std_path)
    lines = [
        "Breadth report",
        "==============",
        f"requirements:   {m['total_requirements']}",
        f"hats total:     {m['total_hats']}",
        f"hats covered:   {m['hats_covered']} ({m['hats_covered'] * 100 // m['total_hats']}%)",
        f"hats missing:   {', '.join(m['hats_uncovered']) or '(none)'}",
        "",
        "Per hat:",
    ]
    for h in sorted(HATS):
        reqs = m["per_hat"].get(h, [])
        bar = "●" * min(len(reqs), 30)
        lines.append(f"  {h:<5} {HATS[h]:<18} {len(reqs):>3}  {bar}")
    lines.append("")
    lines.append("Per section:")
    for s, n in m["per_section"].items():
        lines.append(f"  {s:<24} {n:>3}")
    return "\n".join(lines)  # pragma: no cover
