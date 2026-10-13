"""Apply the distilled math to the live stack."""
from __future__ import annotations

import argparse
import json
import sys

from app.math import graph as gmath
from app.math import phase as pmath
from app.math import som as smath
from app.math import stats as stmath
from app.math.catalog import active, by_target


def run_mesh() -> None:
    from app.mesh.runtime import get_mesh
    m = get_mesh()
    nodes = list(m.graph.nodes.values())
    edges = list(m.graph.edges)
    print("── mesh math ──")
    print(f"  nodes={len(nodes)}  edges={len(edges)}")
    print(f"  fiedler      {gmath.fiedler(nodes, edges)}")
    print(f"  modularity   {gmath.modularity(nodes, edges, attr='kind')}")
    print(f"  clustering   {gmath.clustering_and_path(nodes, edges)}")


def run_flock(n: int = 12, ticks: int = 40) -> None:
    from app.murmur.flock import Flock
    print("── flock math ──")
    flock = Flock(n=n)
    snapshots = []
    for _ in range(ticks):
        flock.tick(dt=0.05)
        snapshots.append(pmath.phases_from_positions(
            [a.state.position.get("signal", 0.0) for a in flock.agents]))
    print(f"  kuramoto_R   {pmath.kuramoto_R(snapshots[-1])}")
    if len(flock.agents) >= 2:
        print(f"  plv(first,last) {pmath.plv(snapshots[-1], snapshots[0])}")
    positions = [a.state.position.get("signal", 0.0) for a in flock.agents]
    upd = smath.som_update(positions, target=0.0,
                            learning_rate=0.3, sigma=1.5)
    mb = sum(positions) / len(positions)
    ma = sum(upd["updated"]) / len(upd["updated"])
    print(f"  som_update   c={upd['c']} "
          f"mean_before={mb:.4f} mean_after={ma:.4f}")


def run_stats() -> None:
    print("── stats math ──")
    print(f"  bonferroni   {stmath.bonferroni(alpha=0.05, m=20)}")
    ps = [0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074,
          0.205, 0.212, 0.216, 0.222, 0.251, 0.269, 0.275,
          0.34, 0.341, 0.384, 0.569, 0.594, 0.696]
    bh = stmath.benjamini_hochberg(ps, alpha=0.05)
    print(f"  BH rejected  {bh['rejected']} of {bh['m']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="math")
    p.add_argument("--mesh", action="store_true")
    p.add_argument("--flock", action="store_true")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--catalog", action="store_true")
    p.add_argument("--target", default=None)
    a = p.parse_args(argv)

    if a.catalog:
        rows = by_target(a.target) if a.target else active()
        print(json.dumps(rows, indent=2))
        return 0

    ran = False
    if a.mesh:
        run_mesh(); ran = True
    if a.flock:
        run_flock(); ran = True
    if a.stats:
        run_stats(); ran = True
    if not ran:
        run_stats()
    return 0


if __name__ == "__main__":
    sys.exit(main())
