"""Demo: parallel dynamic difference engines."""
from __future__ import annotations

import sys

from app.engines.driver import Driver
from app.engines.kinds import list_kinds, list_solvers


def _hdr(t):
    print("=" * 72)
    print("  " + t)
    print("=" * 72)


def main():
    _hdr("registered kinds and solvers")
    for k in list_kinds():
        print(f"  {k:12s}  solvers: {list_solvers(k)}")
    print()

    _hdr("running 4 generations of parallel grids")
    d = Driver(puzzles_per_tile=4, generations=4, seed=0,
               high=0.85, low=0.25)
    result = d.run()

    for g in result["generations"]:
        print(f"  gen {g['index']}  "
              f"difficulty={g['difficulty']}  "
              f"duration={g['duration_ms']:.1f}ms")
        for k, r in sorted(g["rate_by_kind"].items()):
            print(f"    {k:12s} mean_rate={r:.3f}")
    print()

    _hdr("dynamic difficulty trajectory")
    dh = result["difficulty_history"]
    for i, snap in enumerate(dh["history"]):
        print(f"  g{i}:  {snap}")
    print()

    _hdr("difference engine per kind")
    for k, d_ in result["difference"].items():
        print(f"  {k}")
        print(f"    generations:  {d_['generations']}")
        print(f"    dominant:     {d_['dominant']}")
        print(f"    improving:    {d_['improving']}")
        print("    latest delta:")
        for pair, val in sorted(d_["latest_delta"].items()):
            print(f"      {pair:24s} {val:+.3f}")
    print()

    _hdr("final-generation tiles")
    for k, t in sorted(result["final_tiles"].items()):
        print(f"  {k:24s}  trials={t['trials']} "
              f"passes={t['passes']} rate={t['rate']:.3f}")

    print()
    print("=" * 72)
    print("  Parallel: (kind x solver x puzzle) in a thread pool.")
    print("  Dynamic:  difficulty rises when mean_rate > 0.85, falls")
    print("            when mean_rate < 0.25.")
    print("  Difference engine: Level 1 = per-solver rate, Level 2 =")
    print("            pairwise delta, Level 3 = delta-of-delta.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
