"""Parallel training + mesh resolution."""
from __future__ import annotations
import json, sys

from app.train.core import TrainConfig
from app.train.driver import TrainDriver


def _hdr(t):
    print("=" * 74)
    print("  " + t)
    print("=" * 74)


def main():
    _hdr("parallel training — one resolution")
    cfg = TrainConfig(
        kinds=["sudoku", "crossword", "rubik", "tictactoe", "gridworld"],
        difficulties=["easy", "medium", "hard"],
        puzzles_per_tile=2,
        seed=0,
        max_workers=16,
    )
    d = TrainDriver(cfg=cfg, generations=3)
    result = d.run()

    for g in result["generations"]:
        run = g["run"]
        print(f"  gen {g['index']}  "
              f"digest={run['digest']}  "
              f"duration={run['duration_ms']:.0f}ms  "
              f"tiles={len(run['tiles'])}")
        cd = g["cd"]
        print(f"    CD level={cd['level']}  "
              f"n_coords={cd['n_coordinates']}")
        pub = g["publish"]
        print(f"    publish: hops={pub['hops']} "
              f"bits={pub['bits']} "
              f"decoded_ok={pub['decoded_ok']} "
              f"phase_ref=({pub['phase_ref_hi']:.6g}, "
              f"{pub['phase_ref_lo']:+.3e})")
        delta_keys = sorted(g["delta_from_prev"].keys())
        rising = [(k, v) for k, v in g["delta_from_prev"].items() if v > 0]
        falling = [(k, v) for k, v in g["delta_from_prev"].items() if v < 0]
        if rising:
            print(f"    rising:  {rising[:4]}")
        if falling:
            print(f"    falling: {falling[:4]}")
    print()

    _hdr("mesh resolution")
    mesh = result["mesh"]
    print(f"  runs={mesh['runs']}  outcomes={mesh['size']}")
    print(f"  digests={mesh['digests']}")

    _hdr("criss-cross (digest zigzag)")
    for cc in result["criss_cross"]:
        print(f"  {cc['a_index']}x{cc['b_index']}  "
              f"combined={cc['combined']}  length={cc['length']}")

    _hdr("trans (prefix closure)")
    tr = result["trans"]
    print(f"  digests={len(tr['digests'])}  edges={tr['edges']}  "
          f"transitive_pairs={tr['transitive_pairs']}")
    for k, v in tr["reach"].items():
        print(f"    {k} -> {len(v)} reachable")

    _hdr("pollinate (cross-product of tiles)")
    pl = result["pollinate"]
    print(f"  pairs={len(pl)}")
    for p in pl[:12]:
        print(f"    {p['kind']:10s} {p['difficulty']:6s}  "
              f"{p['a_solver']:8s}({p['a_rate']:.2f}) vs "
              f"{p['b_solver']:8s}({p['b_rate']:.2f})  "
              f"delta={p['delta']:+.3f}")

    print()
    print("=" * 74)
    print("  resolution: one CD vector per generation, published as")
    print("  hopping schedules, woven into a single mesh, cross-")
    print("  pollinated pairwise, and content-addressed by digest.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
