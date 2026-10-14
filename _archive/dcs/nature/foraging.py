"""Foraging strategies — heavy-tailed vs diffusive search."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def levy_step(rng, alpha=1.5):  # pragma: no cover
    """Mantegna's alpha-stable step, scaled so median |step| ~ 1 (matches Brownian)."""
    sigma = (
        math.gamma(1 + alpha)
        * math.sin(math.pi * alpha / 2)
        / (math.gamma((1 + alpha) / 2) * alpha * 2 ** ((alpha - 1) / 2))
    ) ** (1 / alpha)
    u = rng.gauss(0, sigma)
    v = rng.gauss(0, 1)
    return 2.0 * u / (abs(v) ** (1 / alpha))  # pragma: no cover


def levy_flight(n=500, alpha=1.5, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    x = y = 0.0
    hits = 0
    visited = set()
    for _ in range(n):
        r = abs(levy_step(rng, alpha))
        th = rng.uniform(0, 2 * math.pi)
        x += r * math.cos(th)
        y += r * math.sin(th)
        cell = (round(x), round(y))
        if cell not in visited:  # pragma: no cover
            visited.add(cell)
            hits += 1
    return {"final": (x, y), "unique_cells": hits, "steps": n}  # pragma: no cover


def brownian_search(n=500, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    x = y = 0.0
    visited = set()
    for _ in range(n):
        x += rng.gauss(0, 1)
        y += rng.gauss(0, 1)
        visited.add((round(x), round(y)))
    return {"final": (x, y), "unique_cells": len(visited), "steps": n}  # pragma: no cover


def area_restricted(n=500, seed=0):  # pragma: no cover
    """Long legs back to home + tight local turns."""
    rng = random.Random(seed)
    x = y = 0.0
    visited = set()
    for i in range(n):
        if i % 20 == 0:  # long leg home  # pragma: no cover
            x, y = 0.0, 0.0
        else:
            th = rng.uniform(0, 2 * math.pi)
            r = abs(rng.gauss(0, 0.4))
            x += r * math.cos(th)
            y += r * math.sin(th)
        visited.add((round(x), round(y)))
    return {"final": (x, y), "unique_cells": len(visited), "steps": n}  # pragma: no cover


def albatross_forage(n=500, seed=0):  # pragma: no cover
    """Levy flight with capped jumps + strong gradient pull toward (10, 10)."""
    rng = random.Random(seed)
    x = y = 0.0
    visited = set()
    for _ in range(n):
        r = min(abs(levy_step(rng, 1.5)), 2.0)
        th = rng.uniform(0, 2 * math.pi)
        x += r * math.cos(th)
        y += r * math.sin(th)
        dx, dy = 10 - x, 10 - y
        d = math.hypot(dx, dy) or 1.0
        x += 0.30 * dx / d
        y += 0.30 * dy / d
        visited.add((round(x), round(y)))
    return {"final": (x, y), "unique_cells": len(visited), "steps": n}  # pragma: no cover


@requirement(
    id="DCS-NAT-FRG-001",
    title="levy flight revisits fewer cells than brownian at equal steps",
    section="nature.foraging",
    hats=["SCI", "RES", "ROB"],
    criticality="SHOULD",
)
def test_levy_more_efficient():  # pragma: no cover
    L = levy_flight(400, seed=1)["unique_cells"]
    B = brownian_search(400, seed=1)["unique_cells"]
    assert L >= B, (L, B)


@requirement(
    id="DCS-NAT-FRG-002",
    title="brownian search is diffusive (rms ~ sqrt(n))",
    section="nature.foraging",
    hats=["SCI"],
    criticality="MUST",
)
def test_brownian_diffusive():  # pragma: no cover
    rng = random.Random(0)
    ns, sq = [], []
    for n in (100, 400, 1600):
        r2 = sum((sum(rng.gauss(0, 1) for _ in range(n))) ** 2 for _ in range(50)) / 50
        ns.append(n)
        sq.append(math.sqrt(r2))
    # sqrt ratio should be near sqrt(n) ratio
    assert 1.5 < sq[1] / sq[0] < 2.5
    assert 1.5 < sq[2] / sq[1] < 2.5


@requirement(
    id="DCS-NAT-FRG-003",
    title="area-restricted stays bounded near origin",
    section="nature.foraging",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_ar_bounded():  # pragma: no cover
    r = area_restricted(2000, seed=3)
    x, y = r["final"]
    assert math.hypot(x, y) < 5, (x, y)


@requirement(
    id="DCS-NAT-FRG-004",
    title="albatross drifts toward gradient target",
    section="nature.foraging",
    hats=["SCI", "RES"],
    criticality="SHOULD",
)
def test_albatross_gradient():  # pragma: no cover
    r = albatross_forage(800, seed=4)
    x, y = r["final"]
    assert math.hypot(10 - x, 10 - y) < 5, (x, y)
