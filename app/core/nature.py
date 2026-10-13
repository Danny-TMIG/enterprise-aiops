"""Observable phenomena in nature, wired as first-class capabilities.

Each phenomenon is a small LOCAL rule. Running it produces behavior.
Catalog: data/nature.tsv (88 rows). Implementations: the ones below.

The dispatchable ones self-register as capabilities of the form
`nature_<code>`. All the rest are catalog-only -- no fake implementations.

No global optimizer. No controller. Local rules only.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

# ── catalog ─────────────────────────────────────────────────────────
CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nature.tsv"


def load_catalog() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if CATALOG_PATH.exists():
        for line in CATALOG_PATH.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                rows.append({"code": parts[0], "class": parts[1],
                             "rule": parts[2]})
    return rows


# ── foraging ────────────────────────────────────────────────────────
def levy_flight(n: int = 1000, alpha: float = 1.5,
                seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    x, y = 0.0, 0.0
    for _ in range(n):
        theta = rng.uniform(0, 2*math.pi)
        step = rng.random() ** (-1.0/alpha)
        step = min(step, 1e6)
        x += step * math.cos(theta)
        y += step * math.sin(theta)
    return {"n": n, "alpha": alpha, "end": [x, y]}


def brownian_search(n: int = 1000, sigma: float = 1.0,
                    seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    x = y = 0.0
    for _ in range(n):
        x += rng.gauss(0, sigma)
        y += rng.gauss(0, sigma)
    return {"n": n, "end": [x, y]}


def area_restricted(n: int = 200, leg: int = 20, turn_sd: float = 1.2,
                    seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    x = y = 0.0; h = 0.0
    for i in range(n):
        if i % leg == 0:
            h = rng.uniform(0, 2*math.pi)
        else:
            h += rng.gauss(0, turn_sd)
        x += math.cos(h); y += math.sin(h)
    return {"n": n, "leg": leg, "end": [x, y]}


def correlated_walk(n: int = 1000, kappa: float = 0.9,
                    seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    x = y = 0.0; h = rng.uniform(0, 2*math.pi)
    for _ in range(n):
        h += rng.gauss(0, math.sqrt(2*(1-kappa)))
        x += math.cos(h); y += math.sin(h)
    return {"n": n, "kappa": kappa, "end": [x, y]}


# ── flocking ────────────────────────────────────────────────────────
def boids(n: int = 40, steps: int = 80, sep: float = 1.5,
          ali: float = 0.05, coh: float = 0.005,
          seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    pos = [[rng.uniform(0, 30), rng.uniform(0, 30)] for _ in range(n)]
    vel = [[rng.gauss(0, 1), rng.gauss(0, 1)] for _ in range(n)]
    for _ in range(steps):
        nv = []
        for i in range(n):
            sx = sy = ax = ay = cx = cy = 0.0; ns = na = nc = 0
            for j in range(n):
                if i == j: continue
                dx = pos[i][0] - pos[j][0]; dy = pos[i][1] - pos[j][1]
                d = math.hypot(dx, dy) + 1e-9
                if d < sep: sx += dx/d; sy += dy/d; ns += 1
                if d < 5.0:
                    ax += vel[j][0]; ay += vel[j][1]; na += 1
                    cx += pos[j][0]; cy += pos[j][1]; nc += 1
            vx, vy = vel[i]
            if ns: vx += (sx/ns)*0.3; vy += (sy/ns)*0.3
            if na: vx += ((ax/na)-vx)*ali; vy += ((ay/na)-vy)*ali
            if nc:
                vx += ((cx/nc)-pos[i][0])*coh
                vy += ((cy/nc)-pos[i][1])*coh
            nv.append([vx, vy])
        for i in range(n):
            pos[i][0] += vel[i][0]*0.1
            pos[i][1] += vel[i][1]*0.1
        vel = nv
    # simple order parameter: mean alignment
    svx = sum(v[0] for v in vel); svy = sum(v[1] for v in vel)
    sv = math.hypot(svx, svy) + 1e-9
    mags = sum(math.hypot(*v) for v in vel) + 1e-9
    return {"n": n, "steps": steps, "order": sv/mags,
            "sample": pos[:3]}


# ── stigmergy ───────────────────────────────────────────────────────
def termite_mound(n: int = 200, steps: int = 200, evap: float = 0.05,
                  seed: int = 0) -> dict[str, Any]:
    """Deposit + follow + evaporate. Gives pile-up structure."""
    rng = random.Random(seed)
    grid = defaultdict(float)
    W = 20
    pos = [[rng.randint(0, W-1), rng.randint(0, W-1)] for _ in range(n)]
    for _ in range(steps):
        for i in range(n):
            x, y = pos[i]
            grid[(x, y)] += 1.0
            # follow rising gradient
            best = (x, y); bestv = grid[(x, y)]
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = (x+dx) % W, (y+dy) % W
                if grid[(nx, ny)] > bestv:
                    bestv = grid[(nx, ny)]; best = (nx, ny)
            pos[i] = list(best)
        for k in list(grid):
            grid[k] *= (1 - evap)
    peak = max(grid.values()) if grid else 0.0
    return {"n": n, "steps": steps, "peak": peak}


def ant_colony(edges: list[tuple[str, str, float]] | None = None,
               source: str = "A", target: str = "E",
               ants: int = 20, steps: int = 40,
               evap: float = 0.1, seed: int = 0) -> dict[str, Any]:
    if edges is None:
        edges = [("A","B",1.0),("A","C",1.5),("B","D",1.0),
                 ("C","D",1.2),("D","E",1.0),("B","E",3.0),
                 ("C","E",2.5),("A","D",2.2)]
    rng = random.Random(seed)
    neighbors: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for a, b, L in edges:
        neighbors[a].append((b, L))
        neighbors[b].append((a, L))
    pheromone: dict[tuple[str, str], float] = defaultdict(lambda: 1.0)
    best = None; best_len = float("inf")
    for _ in range(steps):
        for _ in range(ants):
            node = source; plen = 0.0
            path = [node]; seen = {node}
            for _ in range(200):
                if node == target: break
                opts = [(nb, L) for nb, L in neighbors[node] if nb not in seen]
                if not opts: break
                weights = [(L, (pheromone[(node, nb)] ** 2) / max(L, 1e-6))
                           for nb, L in opts]
                tot = sum(w for _, w in weights)
                if tot <= 0:
                    nb, L = rng.choice(opts)
                else:
                    r = rng.random() * tot; acc = 0.0; nb, L = opts[0]
                    for (nb2, L2), (_, w) in zip(opts, weights):
                        acc += w
                        if r <= acc:
                            nb, L = nb2, L2; break
                path.append(nb); plen += L; seen.add(nb); node = nb
            if node == target and plen < best_len:
                best = list(path); best_len = plen
            if node == target:
                for i in range(len(path)-1):
                    k = (path[i], path[i+1])
                    pheromone[k] += 1.0 / max(plen, 1e-6)
                    pheromone[(path[i+1], path[i])] = pheromone[k]
        for k in list(pheromone):
            pheromone[k] *= (1 - evap)
    return {"best_path": best, "best_len": best_len}


# ── morpho ──────────────────────────────────────────────────────────
def turing_pattern(n: int = 48, steps: int = 300,
                   f: float = 0.055, k: float = 0.062,
                   Da: float = 1.0, Db: float = 0.5,
                   seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    A = [[1.0]*n for _ in range(n)]
    B = [[0.0]*n for _ in range(n)]
    # standard Gray-Scott init (Pearson 1993): one hot patch, sized
    # proportionally to n so the reaction has time to ignite before
    # boundary diffusion washes it out.
    size = max(4, n // 8)
    cx = n // 2
    cy = n // 2
    for i in range(cx - size, cx + size):
        for j in range(cy - size, cy + size):
            if 0 <= i < n and 0 <= j < n:
                A[i][j] = 0.5
                B[i][j] = 0.25 + 0.4 * rng.random()
    # stability: 4*max(Da,Db)*dt < 1  ->  dt <= 0.2 for Da=1.0
    dt = 0.2
    for _ in range(steps):
        nA = [[0.0]*n for _ in range(n)]
        nB = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                a = A[i][j]; b = B[i][j]
                lA = (A[(i-1)%n][j] + A[(i+1)%n][j]
                      + A[i][(j-1)%n] + A[i][(j+1)%n] - 4*a)
                lB = (B[(i-1)%n][j] + B[(i+1)%n][j]
                      + B[i][(j-1)%n] + B[i][(j+1)%n] - 4*b)
                abb = a*b*b
                nA[i][j] = a + (Da*lA - abb + f*(1-a))*dt
                nB[i][j] = b + (Db*lB + abb - (k+f)*b)*dt
        A, B = nA, nB
    flat = [B[i][j] for i in range(n) for j in range(n)]
    mean = sum(flat) / len(flat)
    var = sum((x - mean)**2 for x in flat) / len(flat)
    mx = max(flat)
    return {"n": n, "steps": steps,
            "B_mean": mean, "B_var": var, "B_max": mx,
            "pattern_formed": var > 1e-4}


# ── oscillator ──────────────────────────────────────────────────────
def kuramoto(n: int = 100, steps: int = 200, K: float = 2.0,
             seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    omega = [rng.gauss(0, 1) for _ in range(n)]
    theta = [rng.uniform(0, 2*math.pi) for _ in range(n)]
    dt = 0.05; Rs: list[float] = []
    for _ in range(steps):
        sx = sum(math.cos(t) for t in theta)
        sy = sum(math.sin(t) for t in theta)
        r = math.hypot(sx, sy)/n
        psi = math.atan2(sy, sx)
        theta = [t + dt*(omega[i] + K*r*math.sin(psi - t))
                 for i, t in enumerate(theta)]
        Rs.append(r)
    return {"n": n, "K": K, "R_final": Rs[-1]}


def fitzhugh_nagumo(steps: int = 400, a: float = 0.7, b: float = 0.8,
                    tau: float = 12.5, I: float = 0.5
                    ) -> dict[str, Any]:
    v = w = 0.0; dt = 0.05; spikes = 0; prev = v
    for _ in range(steps):
        dv = v - v**3/3 - w + I
        dw = (v + a - b*w) / tau
        v += dt*dv; w += dt*dw
        if prev < 1.0 and v >= 1.0:
            spikes += 1
        prev = v
    return {"steps": steps, "I": I, "spikes": spikes}


def firefly_sync(n: int = 30, steps: int = 200,
                 seed: int = 0) -> dict[str, Any]:
    """Pulse-coupled: every cycle each firefly nudges its phase toward
    the mean. Order parameter rises."""
    rng = random.Random(seed)
    phase = [rng.uniform(0, 1) for _ in range(n)]
    order_trace: list[float] = []
    for _ in range(steps):
        # advance
        for i in range(n):
            phase[i] = (phase[i] + 0.01) % 1.0
            if phase[i] < 0.01:
                phase[i] = 0.0
                # nudge neighbours
                for j in range(n):
                    if i != j:
                        phase[j] = (phase[j] + 0.005) % 1.0
        # order = |mean(exp(2pi i phase))|
        sx = sum(math.cos(2*math.pi*p) for p in phase)
        sy = sum(math.sin(2*math.pi*p) for p in phase)
        order_trace.append(math.hypot(sx, sy)/n)
    return {"n": n, "steps": steps, "order_final": order_trace[-1]}


# ── walks ───────────────────────────────────────────────────────────
def elephant_walk(n: int = 1000, p: float = 0.5,
                  seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    x = 0.0; history: list[float] = []
    for _ in range(n):
        if not history or rng.random() < p:
            step = 1.0 if rng.random() < 0.5 else -1.0
        else:
            step = rng.choice(history)
        history.append(step); x += step
    return {"n": n, "p": p, "end": x}


def self_avoiding_walk(n: int = 200, seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    visited = {(0, 0)}
    x = y = 0
    for _ in range(n):
        opts = []
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            if (x+dx, y+dy) not in visited:
                opts.append((dx, dy))
        if not opts:
            break
        dx, dy = rng.choice(opts)
        x += dx; y += dy; visited.add((x, y))
    return {"steps": len(visited)-1, "end": [x, y]}


# ── threshold ───────────────────────────────────────────────────────
def quorum_sensing(n: int = 50, threshold: float = 0.5,
                   seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    s = 0.0; at = None
    for step in range(n):
        s += rng.uniform(0, 1)/n
        if at is None and s >= threshold:
            at = step
    return {"n": n, "threshold": threshold, "triggered_at": at, "final": s}


def neuron_threshold(v_th: float = 1.0, steps: int = 200,
                     I: float = 0.02, leak: float = 0.05,
                     seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    v = 0.0; spikes = 0
    for _ in range(steps):
        v += I + rng.gauss(0, 0.005) - leak*v
        if v >= v_th:
            spikes += 1; v = 0.0
    return {"steps": steps, "I": I, "spikes": spikes}


# ── adaptation ──────────────────────────────────────────────────────
def hebbian(n: int = 10, steps: int = 100, lr: float = 0.01,
            seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    W = [[0.0]*n for _ in range(n)]
    for _ in range(steps):
        x = [1.0 if rng.random() < 0.5 else -1.0 for _ in range(n)]
        c = 1.0 if rng.random() < 0.5 else -1.0
        x[0] = x[1] = x[2] = c
        for i in range(n):
            for j in range(n):
                if i != j:
                    W[i][j] += lr * x[i] * x[j]
    intra = (W[0][1] + W[0][2] + W[1][2])/3
    rest = sum(W[i][j] for i in range(3, n) for j in range(3, n) if i != j)
    denom = max(1, (n-3)*(n-4))
    return {"n": n, "steps": steps,
            "avg_correlated": intra, "avg_other": rest/denom}


def homeostat(target: float = 1.0, steps: int = 200,
              gain: float = 0.1, seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    x = 0.0
    for _ in range(steps):
        err = target - x
        x += gain*err + rng.gauss(0, 0.02)
    return {"steps": steps, "target": target, "final": x}


def bacterial_chemotaxis(steps: int = 200, seed: int = 0
                         ) -> dict[str, Any]:
    """Run-and-tumble: if gradient is good, keep running; else tumble."""
    rng = random.Random(seed)
    x = y = 0.0; h = 0.0; last = 0.0
    def field(x, y): return math.exp(-(x*x + y*y)/50.0)
    for _ in range(steps):
        f = field(x, y)
        if f >= last - 1e-9:
            # keep running
            pass
        else:
            # tumble
            h += rng.uniform(-math.pi, math.pi)
        x += math.cos(h); y += math.sin(h)
        last = f
    return {"steps": steps, "end": [x, y], "field": last}


# ── population ──────────────────────────────────────────────────────
def lotka_volterra(steps: int = 400, alpha: float = 1.1, beta: float = 0.4,
                   gamma: float = 0.4, delta: float = 0.1,
                   x0: float = 10.0, y0: float = 5.0
                   ) -> dict[str, Any]:
    dt = 0.01; x = x0; y = y0
    xs = [x]; ys = [y]
    for _ in range(steps):
        dx = alpha*x - beta*x*y
        dy = delta*x*y - gamma*y
        x += dt*dx; y += dt*dy
        xs.append(x); ys.append(y)
    return {"steps": steps, "x_final": x, "y_final": y,
            "x_range": [min(xs), max(xs)], "y_range": [min(ys), max(ys)]}


def logistic(r: float = 0.9, K: float = 100.0, x0: float = 1.0,
             steps: int = 200) -> dict[str, Any]:
    dt = 0.05; x = x0
    for _ in range(steps):
        x += dt * r * x * (1 - x/K)
    return {"r": r, "K": K, "x_final": x}


def sir(S0: float = 0.99, I0: float = 0.01, R0: float = 0.0,
        beta: float = 0.3, gamma: float = 0.1,
        steps: int = 300) -> dict[str, Any]:
    S, I, R = S0, I0, R0; dt = 0.1
    peak_I = I
    for _ in range(steps):
        dS = -beta*S*I
        dI = beta*S*I - gamma*I
        dR = gamma*I
        S += dt*dS; I += dt*dI; R += dt*dR
        peak_I = max(peak_I, I)
    return {"steps": steps, "S_final": S, "I_final": I, "R_final": R,
            "peak_I": peak_I}


# ── flow ────────────────────────────────────────────────────────────
def fick_1d(n: int = 64, steps: int = 200, D: float = 0.5,
            seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed)
    c = [0.0]*n
    for i in range(n//2 - 3, n//2 + 3):
        c[i] = 1.0
    dt = 0.1
    for _ in range(steps):
        nc = list(c)
        for i in range(1, n-1):
            nc[i] = c[i] + D*dt*(c[i-1] - 2*c[i] + c[i+1])
        c = nc
    return {"n": n, "steps": steps, "peak": max(c),
            "spread_center": c[n//2]}


def kirchhoff(nodes: int = 6, seed: int = 0) -> dict[str, Any]:
    """Steady-state currents in a resistor network. Small linear solve."""
    rng = random.Random(seed)
    # build a random graph with conductances
    edges = []
    for i in range(nodes - 1):
        edges.append((i, i+1, rng.uniform(0.5, 2.0)))
    for _ in range(nodes):
        a = rng.randrange(nodes); b = rng.randrange(nodes)
        if a != b:
            edges.append((a, b, rng.uniform(0.5, 2.0)))
    # Laplacian
    L = [[0.0]*nodes for _ in range(nodes)]
    for a, b, g in edges:
        L[a][a] += g; L[b][b] += g
        L[a][b] -= g; L[b][a] -= g
    # ground node 0, inject 1 at last node
    n = nodes - 1
    A = [[L[i+1][j+1] for j in range(n)] for i in range(n)]
    b = [0.0]*n; b[-1] = 1.0
    # gaussian elimination
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[piv] = M[piv], M[i]
        if abs(M[i][i]) < 1e-12:
            continue
        for r in range(i+1, n):
            f = M[r][i]/M[i][i]
            for c in range(i, n+1):
                M[r][c] -= f*M[i][c]
    v = [0.0]*n
    for i in reversed(range(n)):
        s = M[i][n] - sum(M[i][j]*v[j] for j in range(i+1, n))
        v[i] = s/M[i][i] if abs(M[i][i]) > 1e-12 else 0.0
    return {"nodes": nodes, "edges": len(edges), "V": [0.0] + v}


# ── registry: dispatchable phenomena ────────────────────────────────
PHENOMENA: dict[str, tuple[Callable[..., Any], str, str]] = {
    "nature_levy_flight":          (levy_flight,         "foraging",  "heavy-tailed search"),
    "nature_brownian_search":      (brownian_search,     "foraging",  "diffusive search"),
    "nature_area_restricted":      (area_restricted,     "foraging",  "long legs + tight turns"),
    "nature_correlated_walk":      (correlated_walk,     "walk",      "momentum persists"),
    "nature_boids":                (boids,               "flocking",  "sep + ali + coh"),
    "nature_termite_mound":        (termite_mound,       "stigmergy", "deposit + follow + evaporate"),
    "nature_ant_colony":           (ant_colony,          "stigmergy", "pheromone trail"),
    "nature_turing_pattern":       (turing_pattern,      "morpho",    "reaction-diffusion"),
    "nature_kuramoto":             (kuramoto,            "oscillator","mean-field phase coupling"),
    "nature_fitzhugh_nagumo":      (fitzhugh_nagumo,     "oscillator","fast-slow excitable"),
    "nature_firefly_sync":         (firefly_sync,        "oscillator","pulse-coupled sync"),
    "nature_elephant_walk":        (elephant_walk,       "walk",      "memory random walk"),
    "nature_self_avoiding_walk":   (self_avoiding_walk,  "walk",      "no revisits"),
    "nature_quorum_sensing":       (quorum_sensing,      "threshold", "density gate"),
    "nature_neuron_threshold":     (neuron_threshold,    "threshold", "integrate-and-fire"),
    "nature_hebbian":              (hebbian,             "adaptation","fire together, wire together"),
    "nature_homeostat":            (homeostat,           "adaptation","negative feedback"),
    "nature_bacterial_chemotaxis": (bacterial_chemotaxis,"adaptation","run-and-tumble"),
    "nature_lotka_volterra":       (lotka_volterra,      "population","predator-prey"),
    "nature_logistic":             (logistic,            "population","carrying capacity"),
    "nature_sir":                  (sir,                 "population","epidemic compartments"),
    "nature_fick_1d":              (fick_1d,             "flow",      "flux ~ -gradient"),
    "nature_kirchhoff":            (kirchhoff,           "flow",      "current conservation"),
}


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return
    for code, (fn, cls, rule) in PHENOMENA.items():
        def make(fn=fn, cls=cls, rule=rule, code=code):
            def entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
                out = fn(*args, **kwargs)
                if isinstance(out, dict):
                    out["phenomenon"] = code
                    out["class"] = cls
                    out["rule"] = rule
                return out
            return entry
        register(code)(make())


_self_register()


__all__ = [
    "PHENOMENA",
    "ant_colony",
    "area_restricted",
    "bacterial_chemotaxis",
    "boids",
    "brownian_search",
    "correlated_walk",
    "elephant_walk",
    "fick_1d",
    "firefly_sync",
    "fitzhugh_nagumo",
    "hebbian",
    "homeostat",
    "kirchhoff",
    "kuramoto",
    "levy_flight",
    "load_catalog",
    "logistic",
    "lotka_volterra",
    "neuron_threshold",
    "quorum_sensing",
    "self_avoiding_walk",
    "sir",
    "termite_mound",
    "turing_pattern",
]
