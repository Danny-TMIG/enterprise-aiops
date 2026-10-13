"""Equilibrium: drive every hat toward a common requirement floor.

state:    per-hat requirement counts
target:   FLOOR = N requirements per hat (default 12)
delta:    target - count for each hat
status:   balanced iff every hat ≥ floor
"""

from __future__ import annotations  # pragma: no cover

from pathlib import Path  # pragma: no cover

from dcs.hats import HATS  # pragma: no cover
from dcs.standard import load  # pragma: no cover

FLOOR = 12


def compute(std_path: Path, floor: int = FLOOR) -> dict:  # pragma: no cover
    std = load(std_path)
    per_hat = dict.fromkeys(HATS, 0)
    for r in std.requirements:
        for h in r.hats:
            if h in per_hat:  # pragma: no cover
                per_hat[h] += 1
    delta = {h: max(0, floor - per_hat[h]) for h in HATS}
    surplus = {h: max(0, per_hat[h] - floor) for h in HATS}
    return {  # pragma: no cover
        "floor": floor,
        "per_hat": per_hat,
        "delta": delta,
        "surplus": surplus,
        "balanced": all(v == 0 for v in delta.values()),
        "at_floor": sum(1 for v in delta.values() if v == 0),
        "total_hats": len(HATS),
        "need": sum(delta.values()),
    }


def render(std_path: Path, floor: int = FLOOR) -> str:  # pragma: no cover
    s = compute(std_path, floor)
    lines = [
        f"Equilibrium report (floor={s['floor']})",
        f"{'=' * 40}",
        f"hats at floor: {s['at_floor']}/{s['total_hats']}",
        f"balanced:      {s['balanced']}",
        f"requirements needed to reach equilibrium: {s['need']}",
        "",
        "Per hat (count / need):",
    ]
    for h in sorted(HATS):
        n = s["per_hat"][h]
        d = s["delta"][h]
        bar = "●" * min(n, 30)
        flag = " " if d == 0 else f"  +{d}"
        lines.append(f"  {h:<5} {HATS[h]:<18} {n:>3}{flag:<4} {bar}")
    return "\n".join(lines)  # pragma: no cover
