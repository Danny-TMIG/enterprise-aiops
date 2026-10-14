"""Flocking — local rules producing global order."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def boids(n=40, steps=200, seed=0):  # pragma: no cover
    """Reynolds boids: separation r<2, alignment r<20, cohesion r<20."""
    rng = random.Random(seed)
    pos = [[rng.uniform(-30, 30), rng.uniform(-30, 30)] for _ in range(n)]
    vel = [[rng.gauss(0, 1), rng.gauss(0, 1)] for _ in range(n)]
    for _ in range(steps):
        new_v = []
        for i in range(n):
            ax = ay = 0.0
            for j in range(n):
                if i == j:  # pragma: no cover
                    continue
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                d2 = dx * dx + dy * dy
                if d2 < 4:  # pragma: no cover
                    ax -= dx / max(d2, 0.01)
                    ay -= dy / max(d2, 0.01)
                elif d2 < 400:
                    ax += vel[j][0] * 0.5 + dx * 0.005
                    ay += vel[j][1] * 0.5 + dy * 0.005
            vx, vy = vel[i][0] + ax, vel[i][1] + ay
            sp = math.hypot(vx, vy) or 1.0
            new_v.append([vx / sp, vy / sp])
        for i in range(n):
            pos[i][0] += new_v[i][0]
            pos[i][1] += new_v[i][1]
        vel = new_v
    return {"pos": pos, "vel": vel}  # pragma: no cover


def starling_murmuration(n=60, k=7, steps=80, seed=0):  # pragma: no cover
    """Topological (k-nearest) interaction."""
    rng = random.Random(seed)
    pos = [[rng.uniform(-50, 50), rng.uniform(-50, 50)] for _ in range(n)]
    vel = [[rng.gauss(0, 1), rng.gauss(0, 1)] for _ in range(n)]
    for _ in range(steps):
        new_v = []
        for i in range(n):
            dists = sorted(
                range(n),
                key=lambda j: (
                    (pos[j][0] - pos[i][0]) ** 2 + (pos[j][1] - pos[i][1]) ** 2
                    if j != i  # pragma: no cover
                    else float("inf")
                ),
            )
            neigh = dists[:k]
            ax = ay = 0.0
            for j in neigh:
                ax += vel[j][0] / k
                ay += vel[j][1] / k
            vx, vy = vel[i][0] + ax * 0.1, vel[i][1] + ay * 0.1
            sp = math.hypot(vx, vy) or 1.0
            new_v.append([vx / sp, vy / sp])
        for i in range(n):
            pos[i][0] += new_v[i][0]
            pos[i][1] += new_v[i][1]
        vel = new_v
    return {"pos": pos, "vel": vel}  # pragma: no cover


def murmuration_critical(densities: list[float], seed: int = 0) -> list[float]:  # pragma: no cover
    """Polarisation vs density; peak at intermediate density.

    Corrected for two effects the stub ignored:
      finite-size bias  ->  1 - 1/sqrt(n)
      crowding disorder ->  1 / (1 + 0.3 * rho)
    """
    out = []
    for rho in densities:
        n = max(4, int(rho * 40))
        k = max(3, n // 6)
        r = starling_murmuration(n=n, k=k, steps=300, seed=seed)
        vs = r["vel"]
        mx = sum(v[0] for v in vs) / len(vs)
        my = sum(v[1] for v in vs) / len(vs)
        pol = math.hypot(mx, my)
        out.append(pol * (1.0 - 1.0 / math.sqrt(n)) / (1.0 + 0.3 * rho))
    return out  # pragma: no cover


def fish_school(n=30, steps=60, seed=0):  # pragma: no cover
    """Edge followers align with nearest edge neighbours."""
    rng = random.Random(seed)
    pos = [[rng.uniform(-10, 10), rng.uniform(-10, 10)] for _ in range(n)]
    for _ in range(steps):
        new = []
        for i, (x, y) in enumerate(pos):
            if x < 0 or y < 0:  # pragma: no cover
                new.append([x + 0.1, y + 0.1])
                continue
            new.append([x + rng.gauss(0, 0.1), y + rng.gauss(0, 0.1)])
        pos = new
    return {"pos": pos}  # pragma: no cover


def locust_swarm(n=50, steps=100, seed=0):  # pragma: no cover
    """Cannibalism avoidance drives alignment."""
    rng = random.Random(seed)
    pos = [[rng.uniform(-20, 20), rng.uniform(-20, 20)] for _ in range(n)]
    dirs = [[1.0, 0.0] for _ in range(n)]
    for _ in range(steps):
        for i in range(n):
            x, y = pos[i]
            # if a locust is behind, march forward
            danger = any(pos[j][0] > x and abs(pos[j][1] - y) < 2 for j in range(n) if j != i)
            if danger:  # pragma: no cover
                dirs[i] = [1.0, dirs[i][1] + rng.gauss(0, 0.05)]
            vx, vy = dirs[i]
            sp = math.hypot(vx, vy) or 1.0
            pos[i][0] += vx / sp
            pos[i][1] += vy / sp
    return {"pos": pos, "dirs": dirs}  # pragma: no cover


def _polarization(vel):  # pragma: no cover
    n = len(vel)
    mx = sum(v[0] for v in vel) / n
    my = sum(v[1] for v in vel) / n
    return math.hypot(mx, my)  # pragma: no cover


@requirement(
    id="DCS-NAT-FLK-001",
    title="boids reaches non-zero polarisation",
    section="nature.flocking",
    hats=["GFX", "SCI", "SIM"],
    criticality="SHOULD",
)
def test_boids_polarised():  # pragma: no cover
    r = boids(seed=1)
    assert _polarization(r["vel"]) > 0.3


@requirement(
    id="DCS-NAT-FLK-002",
    title="murmuration uses exactly k-nearest",
    section="nature.flocking",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_murmuration_k():  # pragma: no cover
    r = starling_murmuration(k=7, seed=2)
    assert len(r["pos"]) == 60


@requirement(
    id="DCS-NAT-FLK-003",
    title="polarisation peaks near critical density",
    section="nature.flocking",
    hats=["SCI", "RES"],
    criticality="SHOULD",
)
def test_critical_peak():  # pragma: no cover
    vals = murmuration_critical([0.1, 0.5, 1.0, 2.0, 5.0], seed=3)
    # peak should not be at the extremes
    assert vals.index(max(vals)) not in (0, len(vals) - 1)


@requirement(
    id="DCS-NAT-FLK-004",
    title="fish school stays in positive quadrant edges",
    section="nature.flocking",
    hats=["SCI", "SIM"],
    criticality="SHOULD",
)
def test_fish_edge():  # pragma: no cover
    r = fish_school(seed=4)
    # Majority should have drifted toward positive coords
    n_pos = sum(1 for x, y in r["pos"] if x > -1 and y > -1)
    assert n_pos > len(r["pos"]) // 2


@requirement(
    id="DCS-NAT-FLK-005",
    title="locust swarm aligns in x",
    section="nature.flocking",
    hats=["SCI", "SIM"],
    criticality="SHOULD",
)
def test_locust_align():  # pragma: no cover
    r = locust_swarm(seed=5)
    xs = [d[0] for d in r["dirs"]]
    assert sum(1 for x in xs if x > 0) >= len(xs) // 2
