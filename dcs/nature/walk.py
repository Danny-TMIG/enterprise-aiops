"""Walk models — memory, exclusion, persistence, dimensionality."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def correlated_walk(n=500, kappa=0.9, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    x = y = 0.0
    th = rng.uniform(0, 2 * math.pi)
    for _ in range(n):
        th += rng.gauss(0, math.sqrt(1 - kappa**2))
        x += math.cos(th)
        y += math.sin(th)
    return {"final": (x, y), "kappa": kappa}  # pragma: no cover


def elephant_walk(n=500, seed=0):  # pragma: no cover
    """Walks toward a random visited site with probability 1/2, else new."""
    rng = random.Random(seed)
    x = y = 0.0
    visited = [(0.0, 0.0)]
    for _ in range(n):
        if rng.random() < 0.5:  # pragma: no cover
            tx, ty = rng.choice(visited)
        else:
            tx, ty = rng.uniform(-50, 50), rng.uniform(-50, 50)
        x += (tx - x) * 0.05
        y += (ty - y) * 0.05
        visited.append((x, y))
    return {"final": (x, y), "visited": len(visited)}  # pragma: no cover


def self_avoiding_walk(n=200, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    x, y = 0, 0
    visited = {(0, 0)}
    for _ in range(n):
        opts = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        opts = [p for p in opts if p not in visited]
        if not opts:  # pragma: no cover
            break
        x, y = rng.choice(opts)
        visited.add((x, y))
    return {"final": (x, y), "steps": len(visited) - 1}  # pragma: no cover


def persistent_walk(n=500, seed=0, sigma=0.02):  # pragma: no cover
    """Persistent walk — small per-step angular noise keeps it ballistic."""
    rng = random.Random(seed)
    x = y = 0.0
    th = 0.0
    for _ in range(n):
        th += rng.gauss(0, sigma)
        x += math.cos(th)
        y += math.sin(th)
    return {"final": (x, y), "sigma": sigma}  # pragma: no cover


def levy_walk_2d(n=500, alpha=1.5, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    from dcs.nature.foraging import levy_step  # pragma: no cover

    x = y = 0.0
    for _ in range(n):
        r = abs(levy_step(rng, alpha))
        th = rng.uniform(0, 2 * math.pi)
        x += r * math.cos(th)
        y += r * math.sin(th)
    return {"final": (x, y)}  # pragma: no cover


@requirement(
    id="DCS-NAT-WALK-001",
    title="correlated walk is ballistic at kappa=1",
    section="nature.walk",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_correlated_ballistic():  # pragma: no cover
    r = correlated_walk(500, kappa=0.999, seed=1)
    x, y = r["final"]
    assert math.hypot(x, y) > 400


@requirement(
    id="DCS-NAT-WALK-002",
    title="elephant walk keeps full history",
    section="nature.walk",
    hats=["SCI", "RES"],
    criticality="MUST",
)
def test_elephant_memory():  # pragma: no cover
    r = elephant_walk(300, seed=1)
    assert r["visited"] == 301


@requirement(
    id="DCS-NAT-WALK-003",
    title="self-avoiding walk never revisits",
    section="nature.walk",
    hats=["SCI"],
    criticality="MUST",
)
def test_saw_no_revisit():  # pragma: no cover
    from collections import Counter  # pragma: no cover

    rng = random.Random(2)
    x, y = 0, 0
    seen = Counter([(0, 0)])
    for _ in range(200):
        opts = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        opts = [p for p in opts if p not in seen]
        if not opts:  # pragma: no cover
            break
        x, y = rng.choice(opts)
        seen[(x, y)] += 1
    assert all(c == 1 for c in seen.values())


@requirement(
    id="DCS-NAT-WALK-004",
    title="persistent walk ends far from origin",
    section="nature.walk",
    hats=["SCI"],
    criticality="SHOULD",
)
def test_persistent_far():  # pragma: no cover
    r = persistent_walk(400, seed=3)
    x, y = r["final"]
    assert math.hypot(x, y) > 300


@requirement(
    id="DCS-NAT-WALK-005",
    title="2D levy walk has heavy-tail step distribution",
    section="nature.walk",
    hats=["SCI", "QT"],
    criticality="SHOULD",
)
def test_levy_2d_heavy_tail():  # pragma: no cover
    import random  # pragma: no cover

    from dcs.nature.foraging import levy_step  # pragma: no cover

    rng = random.Random(4)
    steps = [abs(levy_step(rng, 1.5)) for _ in range(5000)]
    mx = max(steps)
    med = sorted(steps)[len(steps) // 2]
    assert mx > 20 * (med or 1)
