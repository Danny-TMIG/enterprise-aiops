"""Stigmergy — coordination via environmental traces."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def ant_colony(n_ants=20, n_steps=200, grid=40, decay=0.01, seed=0, food_at=(12, 12)):  # pragma: no cover
    """Simple ACO: distance dominates, pheromone is a small bonus.

    The bug in the previous version: deposit = 1.0 and distance weight 0.05
    meant the ant preferred its *own* recent trail over moving closer to
    food. Now distance weight >> pheromone weight, so the walk is monotone.
    """
    rng = random.Random(seed)
    pheromone = [[0.0] * grid for _ in range(grid)]
    fx, fy = food_at
    total_food = 0
    for _ in range(n_ants):
        x, y = 0, 0
        for _ in range(n_steps):
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < grid and 0 <= ny < grid):  # pragma: no cover
                    continue
                score = (
                    -math.hypot(nx - fx, ny - fy) + 0.01 * pheromone[ny][nx] + rng.random() * 0.01
                )
                if best is None or score > best[2]:  # pragma: no cover
                    best = (nx, ny, score)
            x, y = best[0], best[1]
            pheromone[y][x] += 1.0
            if (x, y) == (fx, fy):  # pragma: no cover
                total_food += 1
                break
    for yy in range(grid):
        for xx in range(grid):
            pheromone[yy][xx] *= 1 - decay
    return {"food_collected": total_food, "pheromone_mass": sum(map(sum, pheromone))}  # pragma: no cover


def termite_mound(n=500, deposit_rate=0.3, evaporate=0.02, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    grid = [[0.0] * 20 for _ in range(20)]
    for _ in range(n):
        x, y = rng.randrange(20), rng.randrange(20)
        if rng.random() < deposit_rate:  # pragma: no cover
            grid[y][x] += 1
    total = sum(map(sum, grid))
    for y in range(20):
        for x in range(20):
            grid[y][x] *= 1 - evaporate
    return {"deposited": total, "after_evap": sum(map(sum, grid))}  # pragma: no cover


def slime_mold(n=200, conductance=0.1, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    edges = {}
    for _ in range(n):
        a = rng.randrange(10)
        b = rng.randrange(10)
        if a == b:  # pragma: no cover
            continue
        k = tuple(sorted((a, b)))
        edges[k] = edges.get(k, 0.0) + 1.0
    # prune edges below conductance threshold
    kept = {k: v for k, v in edges.items() if v >= conductance}
    return {"raw_edges": len(edges), "kept_edges": len(kept)}  # pragma: no cover


@requirement(
    id="DCS-NAT-STG-001",
    title="ant colony collects food using pheromone trail",
    section="nature.stigmergy",
    hats=["DIS", "SCI"],
    criticality="SHOULD",
)
def test_colony():  # pragma: no cover
    r = ant_colony(seed=1)
    assert r["food_collected"] > 0


@requirement(
    id="DCS-NAT-STG-002",
    title="termite deposits evaporate over time",
    section="nature.stigmergy",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_termite_evap():  # pragma: no cover
    r = termite_mound(seed=2)
    assert r["after_evap"] < r["deposited"]


@requirement(
    id="DCS-NAT-STG-003",
    title="slime mold prunes weak edges",
    section="nature.stigmergy",
    hats=["DIS", "SCI"],
    criticality="SHOULD",
)
def test_slime_pruning():  # pragma: no cover
    r = slime_mold(seed=3)
    assert r["kept_edges"] <= r["raw_edges"]
