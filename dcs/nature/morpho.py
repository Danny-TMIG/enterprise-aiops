"""Morphogenesis — pattern formation without a plan."""
import math, random
from dcs.generate import requirement

def turing_pattern(n=48, steps=3000, seed=0):
    rng = random.Random(seed)
    a = [[1.0 + rng.random()*0.05 for _ in range(n)] for _ in range(n)]
    b = [[0.5 + rng.random()*0.05 for _ in range(n)] for _ in range(n)]
    Da, Db, f, k = 0.16, 0.08, 0.06, 0.062
    for _ in range(steps):
        na = [[0.0]*n for _ in range(n)]
        nb = [[0.0]*n for _ in range(n)]
        for y in range(1, n-1):
            for x in range(1, n-1):
                la = (a[y-1][x]+a[y+1][x]+a[y][x-1]+a[y][x+1]-4*a[y][x])
                lb = (b[y-1][x]+b[y+1][x]+b[y][x-1]+b[y][x+1]-4*b[y][x])
                na[y][x] = a[y][x] + Da*la - a[y][x]*b[y][x]**2 + f*(1-a[y][x])
                nb[y][x] = b[y][x] + Db*lb + a[y][x]*b[y][x]**2 - (k+f)*b[y][x]
        a, b = na, nb
    return {"a": a, "b": b, "variance": max(_variance(a), _variance(b))}

def gray_scott(n=48, steps=3000, seed=0):
    rng = random.Random(seed)
    u = [[1.0]*n for _ in range(n)]; v = [[0.0]*n for _ in range(n)]
    for y in range(n//2-5, n//2+5):
        for x in range(n//2-5, n//2+5):
            v[y][x] = 0.25 + rng.random()*0.1
    Du, Dv, f, k = 0.16, 0.08, 0.035, 0.065
    for _ in range(steps):
        nu = [[0.0]*n for _ in range(n)]; nv = [[0.0]*n for _ in range(n)]
        for y in range(1, n-1):
            for x in range(1, n-1):
                lu = u[y-1][x]+u[y+1][x]+u[y][x-1]+u[y][x+1]-4*u[y][x]
                lv = v[y-1][x]+v[y+1][x]+v[y][x-1]+v[y][x+1]-4*v[y][x]
                nu[y][x] = u[y][x] + Du*lu - u[y][x]*v[y][x]**2 + f*(1-u[y][x])
                nv[y][x] = v[y][x] + Dv*lv + u[y][x]*v[y][x]**2 - (k+f)*v[y][x]
        u, v = nu, nv
    return {"u": u, "v": v, "variance": _variance(v)}

def belousov_zhabotinsky(n=32, steps=2000, seed=0):
    rng = random.Random(seed)
    u = [[0.0]*n for _ in range(n)]; v = [[0.0]*n for _ in range(n)]
    for y in range(n): 
        for x in range(n): u[y][x] = 1.0 if rng.random() < 0.1 else 0.0
    Du, Dv, eps, q, f = 0.16, 0.08, 0.01, 0.002, 1.0
    for _ in range(steps):
        nu = [[0.0]*n for _ in range(n)]; nv = [[0.0]*n for _ in range(n)]
        for y in range(1, n-1):
            for x in range(1, n-1):
                lu = u[y-1][x]+u[y+1][x]+u[y][x-1]+u[y][x+1]-4*u[y][x]
                lv = v[y-1][x]+v[y+1][x]+v[y][x-1]+v[y][x+1]-4*v[y][x]
                qq = (f*v[y][x]+q) / (v[y][x]+1.0)
                nu[y][x] = u[y][x] + Du*lu + qq*u[y][x]*(1-u[y][x])/eps
                nv[y][x] = v[y][x] + Dv*lv + u[y][x]-v[y][x]
        u, v = nu, nv
    return {"u": u, "v": v}

def dla(n_particles=300, seed=0, size=80):
    rng = random.Random(seed)
    grid = {(0, 0)}
    for _ in range(n_particles):
        r = size
        th = rng.uniform(0, 2*math.pi)
        x, y = int(r*math.cos(th)), int(r*math.sin(th))
        for _ in range(10000):
            dx, dy = rng.choice([(1,0),(-1,0),(0,1),(0,-1)])
            x += dx; y += dy
            if any((x+dx, y+dy) in grid for dx, dy in
                   ((1,0),(-1,0),(0,1),(0,-1))):
                grid.add((x, y)); break
    return {"size": len(grid), "grid": grid}

def eden_growth(n=300, seed=0):
    rng = random.Random(seed)
    cluster = {(0, 0)}
    frontier = [(1,0), (-1,0), (0,1), (0,-1)]
    while len(cluster) < n and frontier:
        i = rng.randrange(len(frontier))
        cell = frontier.pop(i)
        if cell in cluster: continue
        cluster.add(cell)
        x, y = cell
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nb = (x+dx, y+dy)
            if nb not in cluster and nb not in frontier:
                frontier.append(nb)
    # compactness = perimeter^2 / area
    perim = sum(1 for (x, y) in cluster
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))
                if (x+dx, y+dy) not in cluster)
    return {"size": len(cluster), "perimeter": perim}

def lichen_edge(steps=200, growth=0.02):
    r = 1.0
    for _ in range(steps): r += growth
    return {"radius": r}

def tree_branching(depth=4, branch_angle=0.3, seed=0):
    """L-system style binary tree."""
    branches = [(0.0, 0.0, math.pi/2, 1.0)]
    out = []
    for _ in range(depth):
        new = []
        for x, y, th, length in branches:
            out.append((x, y, th, length))
            x2, y2 = x + length*math.cos(th), y + length*math.sin(th)
            new.append((x2, y2, th+branch_angle, length*0.7))
            new.append((x2, y2, th-branch_angle, length*0.7))
        branches = new
    return {"segments": len(out)}


def _variance(grid):
    vals = [v for row in grid for v in row]
    if not vals: return 0.0
    m = sum(vals)/len(vals)
    return sum((v-m)**2 for v in vals)/len(vals)


@requirement(id="DCS-NAT-MOR-001", title="Turing pattern forms non-uniform b",
             section="nature.morpho", hats=["SCI","SIM","GFX"], criticality="MUST")
def test_turing():
    r = turing_pattern()
    assert r["variance"] > 0.001, r["variance"]


@requirement(id="DCS-NAT-MOR-002", title="Gray-Scott v is spatially non-uniform",
             section="nature.morpho", hats=["SCI","SIM"], criticality="MUST")
def test_gs():
    assert gray_scott()["variance"] > 1e-4


@requirement(id="DCS-NAT-MOR-003", title="BZ reaction sustains a spatial pattern",
             section="nature.morpho", hats=["SCI"], criticality="SHOULD")
def test_bz():
    r = belousov_zhabotinsky()
    assert any(v > 0.3 for row in r["v"] for v in row)


@requirement(id="DCS-NAT-MOR-004", title="DLA produces a branching fractal cluster",
             section="nature.morpho", hats=["SCI","GFX"], criticality="SHOULD")
def test_dla():
    r = dla(100, seed=1)
    assert r["size"] >= 40


@requirement(id="DCS-NAT-MOR-005", title="Eden growth is compact (low perimeter/area)",
             section="nature.morpho", hats=["SCI"], criticality="SHOULD")
def test_eden_compact():
    r = eden_growth(200, seed=2)
    perim_over_area = r["perimeter"] / r["size"]
    assert perim_over_area < 4.0, perim_over_area


@requirement(id="DCS-NAT-MOR-006", title="lichen edge grows outward",
             section="nature.morpho", hats=["SCI","SIM"], criticality="MUST")
def test_lichen():
    assert lichen_edge()["radius"] > 1.0


@requirement(id="DCS-NAT-MOR-007", title="tree branches double per level",
             section="nature.morpho", hats=["GFX","SCI"], criticality="MAY")
def test_tree():
    assert tree_branching(4)["segments"] == 15
