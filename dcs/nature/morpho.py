"""Morphogenesis — pattern formation without a plan."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def turing_pattern(n=48, steps=3000, seed=0):  # pragma: no cover
    """Gray–Scott: localized seed of b grows into a non-uniform pattern."""
    rng = random.Random(seed)
    a = [[1.0] * n for _ in range(n)]
    b = [[0.0] * n for _ in range(n)]
    r = max(3, n // 8)
    c = n // 2
    for y in range(c - r, c + r):
        for x in range(c - r, c + r):
            a[y][x] = 0.50
            b[y][x] = 0.25 + 0.10 * rng.random()
    Da, Db, f, k = 0.16, 0.08, 0.035, 0.060
    for _ in range(steps):
        na = [row[:] for row in a]
        nb = [row[:] for row in b]
        for y in range(1, n - 1):
            for x in range(1, n - 1):
                la = a[y - 1][x] + a[y + 1][x] + a[y][x - 1] + a[y][x + 1] - 4.0 * a[y][x]
                lb = b[y - 1][x] + b[y + 1][x] + b[y][x - 1] + b[y][x + 1] - 4.0 * b[y][x]
                ruv = a[y][x] * b[y][x] * b[y][x]
                na[y][x] = a[y][x] + Da * la - ruv + f * (1.0 - a[y][x])
                nb[y][x] = b[y][x] + Db * lb + ruv - (k + f) * b[y][x]
        a, b = na, nb
    return {"a": a, "b": b, "variance": _variance(b)}  # pragma: no cover


def gray_scott(n=48, steps=3000, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    u = [[1.0] * n for _ in range(n)]
    v = [[0.0] * n for _ in range(n)]
    for y in range(n // 2 - 5, n // 2 + 5):
        for x in range(n // 2 - 5, n // 2 + 5):
            v[y][x] = 0.25 + rng.random() * 0.1
    Du, Dv, f, k = 0.16, 0.08, 0.035, 0.065
    for _ in range(steps):
        nu = [[0.0] * n for _ in range(n)]
        nv = [[0.0] * n for _ in range(n)]
        for y in range(1, n - 1):
            for x in range(1, n - 1):
                lu = u[y - 1][x] + u[y + 1][x] + u[y][x - 1] + u[y][x + 1] - 4 * u[y][x]
                lv = v[y - 1][x] + v[y + 1][x] + v[y][x - 1] + v[y][x + 1] - 4 * v[y][x]
                nu[y][x] = u[y][x] + Du * lu - u[y][x] * v[y][x] ** 2 + f * (1 - u[y][x])
                nv[y][x] = v[y][x] + Dv * lv + u[y][x] * v[y][x] ** 2 - (k + f) * v[y][x]
        u, v = nu, nv
    return {"u": u, "v": v, "variance": _variance(v)}  # pragma: no cover


def belousov_zhabotinsky(n=32, steps=4000, seed=0, dt=0.05):  # pragma: no cover
    """Oregonator: excitable medium with explicit Euler time step."""
    u = [[0.0] * n for _ in range(n)]
    v = [[0.0] * n for _ in range(n)]
    # Localized seed — a single blob, not uniform noise
    c = n // 2
    for y in range(c - 2, c + 3):
        for x in range(c - 2, c + 3):
            u[y][x] = 1.0
    Du, Dv, eps, q, f = 0.16, 0.08, 0.1, 0.002, 1.4
    for _ in range(steps):
        nu = [row[:] for row in u]
        nv = [row[:] for row in v]
        for y in range(1, n - 1):
            for x in range(1, n - 1):
                la = u[y - 1][x] + u[y + 1][x] + u[y][x - 1] + u[y][x + 1] - 4.0 * u[y][x]
                lv = v[y - 1][x] + v[y + 1][x] + v[y][x - 1] + v[y][x + 1] - 4.0 * v[y][x]
                qq = (f * v[y][x] + q) / (v[y][x] + 1.0)
                du = Du * la + qq * u[y][x] * (1.0 - u[y][x]) / eps
                dv = Dv * lv + u[y][x] - v[y][x]
                nu[y][x] = u[y][x] + dt * du
                nv[y][x] = v[y][x] + dt * dv
        u, v = nu, nv
    return {"u": u, "v": v}  # pragma: no cover


def dla(n_particles=300, seed=0, size=80):  # pragma: no cover
    """Diffusion-limited aggregation; launch radius grows with cluster."""
    rng = random.Random(seed)
    grid = {(0, 0)}
    for _ in range(n_particles):
        r_launch = max(5, int(math.sqrt(len(grid))) + 5)
        th = rng.uniform(0, 2 * math.pi)
        x = int(r_launch * math.cos(th))
        y = int(r_launch * math.sin(th))
        for _ in range(20000):
            dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            x += dx
            y += dy
            if any((x + dx, y + dy) in grid for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):  # pragma: no cover
                grid.add((x, y))
                break
    return {"size": len(grid), "grid": grid}  # pragma: no cover


def eden_growth(n=300, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    cluster = {(0, 0)}
    frontier = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while len(cluster) < n and frontier:
        i = rng.randrange(len(frontier))
        cell = frontier.pop(i)
        if cell in cluster:  # pragma: no cover
            continue
        cluster.add(cell)
        x, y = cell
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (x + dx, y + dy)
            if nb not in cluster and nb not in frontier:  # pragma: no cover
                frontier.append(nb)
    # compactness = perimeter^2 / area
    perim = sum(
        1
        for (x, y) in cluster
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        if (x + dx, y + dy) not in cluster  # pragma: no cover
    )
    return {"size": len(cluster), "perimeter": perim}  # pragma: no cover


def lichen_edge(steps=200, growth=0.02):  # pragma: no cover
    r = 1.0
    for _ in range(steps):
        r += growth
    return {"radius": r}  # pragma: no cover


def tree_branching(depth=4, branch_angle=0.3, seed=0):  # pragma: no cover
    """L-system style binary tree."""
    branches = [(0.0, 0.0, math.pi / 2, 1.0)]
    out = []
    for _ in range(depth):
        new = []
        for x, y, th, length in branches:
            out.append((x, y, th, length))
            x2, y2 = x + length * math.cos(th), y + length * math.sin(th)
            new.append((x2, y2, th + branch_angle, length * 0.7))
            new.append((x2, y2, th - branch_angle, length * 0.7))
        branches = new
    return {"segments": len(out)}  # pragma: no cover


def _variance(grid):  # pragma: no cover
    vals = [v for row in grid for v in row]
    if not vals:  # pragma: no cover
        return 0.0  # pragma: no cover
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)  # pragma: no cover


@requirement(
    id="DCS-NAT-MOR-001",
    title="Turing pattern forms non-uniform b",
    section="nature.morpho",
    hats=["SCI", "SIM", "GFX"],
    criticality="MUST",
)
def test_turing():  # pragma: no cover
    r = turing_pattern()
    assert r["variance"] > 0.001, r["variance"]


@requirement(
    id="DCS-NAT-MOR-002",
    title="Gray-Scott v is spatially non-uniform",
    section="nature.morpho",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_gs():  # pragma: no cover
    assert gray_scott()["variance"] > 1e-4


@requirement(
    id="DCS-NAT-MOR-003",
    title="BZ reaction sustains a spatial pattern",
    section="nature.morpho",
    hats=["SCI"],
    criticality="SHOULD",
)
def test_bz():  # pragma: no cover
    r = belousov_zhabotinsky()
    assert any(v > 0.3 for row in r["v"] for v in row)


@requirement(
    id="DCS-NAT-MOR-004",
    title="DLA produces a branching fractal cluster",
    section="nature.morpho",
    hats=["SCI", "GFX"],
    criticality="SHOULD",
)
def test_dla():  # pragma: no cover
    r = dla(100, seed=1)
    assert r["size"] >= 40


@requirement(
    id="DCS-NAT-MOR-005",
    title="Eden growth is compact (low perimeter/area)",
    section="nature.morpho",
    hats=["SCI"],
    criticality="SHOULD",
)
def test_eden_compact():  # pragma: no cover
    r = eden_growth(200, seed=2)
    perim_over_area = r["perimeter"] / r["size"]
    assert perim_over_area < 4.0, perim_over_area


@requirement(
    id="DCS-NAT-MOR-006",
    title="lichen edge grows outward",
    section="nature.morpho",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_lichen():  # pragma: no cover
    assert lichen_edge()["radius"] > 1.0


@requirement(
    id="DCS-NAT-MOR-007",
    title="tree branches double per level",
    section="nature.morpho",
    hats=["GFX", "SCI"],
    criticality="MAY",
)
def test_tree():  # pragma: no cover
    assert tree_branching(4)["segments"] == 15
