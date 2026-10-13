"""Murmur harness — same output shape as usefulness, so the
observer can parse it identically.

Runs the flock for N ticks, prints one line per agent-run:

    [bits] <agent>-<tick> score=X.XX

where bits are:
    effect_ok / recentered / aligned / verdict_ok / stable / capped
"""
from __future__ import annotations

import sys

from app.murmur.flock import Flock

TICKS = 60
N = 8


def main() -> int:
    print(f"-- murmur -- {N} agents, {TICKS} ticks --")
    flock = Flock(n=N)
    rows = []
    for t in range(TICKS):
        r = flock.tick(dt=0.05)
        for e in r["effects"]:
            rec = 1 if e["decision"] == "act.recenter" else 0
            ali = 1 if e["decision"] == "act.align" else 0
            ok = 1 if e["effect"] else 0
            v = 1 if e["verdict"] else 0
            st = 1 if e["update"] == "reinforce" else 0
            cap = 1 if float(e["alloc_share"]) < 0.1 else 0
            bits = f"{ok}{rec}{ali}{v}{st}{1 - cap}"
            score = sum(int(c) for c in bits) / 6.0
            rows.append((f"{e['agent']}-{t}", bits, score))

    axis = {
        "effect_ok": sum(int(r[1][0]) for r in rows),
        "recentered": sum(int(r[1][1]) for r in rows),
        "aligned": sum(int(r[1][2]) for r in rows),
        "verdict_ok": sum(int(r[1][3]) for r in rows),
        "reinforced": sum(int(r[1][4]) for r in rows),
        "not_capped": sum(int(r[1][5]) for r in rows),
    }
    n = max(1, len(rows))
    print(f"  {'effect_ok':12s} {axis['effect_ok']}/{n}")
    print(f"  {'recentered':12s} {axis['recentered']}/{n}")
    print(f"  {'aligned':12s} {axis['aligned']}/{n}")
    print(f"  {'verdict_ok':12s} {axis['verdict_ok']}/{n}")
    print(f"  {'reinforced':12s} {axis['reinforced']}/{n}")
    print(f"  {'not_capped':12s} {axis['not_capped']}/{n}")

    print()
    for name, bits, score in rows[:10]:
        print(f"  [{bits}] {name:12s} score={score:.2f}")
    for name, bits, score in rows[-10:]:
        print(f"  [{bits}] {name:12s} score={score:.2f}")

    final = flock.last_metrics
    print()
    print(f"  mean_deviation   {final.get('mean_deviation', 0):.4f}")
    print(f"  effect_ok_rate   {final.get('effect_ok_rate', 0):.3f}")
    print(f"  recentered_rate  {final.get('recentered_rate', 0):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
