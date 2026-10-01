"""Population dynamics — growth, cycles, epidemics."""

import math
import random

from dcs.generate import requirement


def logistic(N0, r, K, steps=200, dt=0.05):
    N = N0
    out = []
    for _ in range(steps):
        N += dt * r * N * (1 - N / K)
        out.append(N)
    return out


def gompertz(N0, a, b, steps=200, dt=0.05):
    N = N0
    out = []
    for _ in range(steps):
        N += dt * a * N * math.log(b / N)
        out.append(N)
    return out


def allee(N0, r, K, A, steps=200, dt=0.05):
    N = N0
    out = []
    for _ in range(steps):
        N += dt * r * N * (1 - N / K) * (N - A) / K
        N = max(0, N)
        out.append(N)
    return out


def lotka_volterra(prey0, pred0, a=1.0, b=0.1, c=0.075, d=1.5, steps=4000, dt=0.001):
    x, y = prey0, pred0
    out = []
    for _ in range(steps):
        dx = a * x - b * x * y
        dy = -c * y + d * x * y
        x += dt * dx
        y += dt * dy
        out.append((x, y))
    return out


def sir(S0, I0, R0, beta=0.3, gamma=0.1, steps=500, dt=0.1):
    S, I, R = S0, I0, R0
    out = []
    for _ in range(steps):
        dS = -beta * S * I / (S + I + R + 1e-9)
        dI = beta * S * I / (S + I + R + 1e-9) - gamma * I
        dR = gamma * I
        S += dt * dS
        I += dt * dI
        R += dt * dR
        out.append((S, I, R))
    return out


def sirs(S0, I0, R0, beta=0.4, gamma=0.1, xi=0.02, steps=1000, dt=0.1):
    S, I, R = S0, I0, R0
    out = []
    for _ in range(steps):
        N = S + I + R + 1e-9
        dS = -beta * S * I / N + xi * R
        dI = beta * S * I / N - gamma * I
        dR = gamma * I - xi * R
        S += dt * dS
        I += dt * dI
        R += dt * dR
        out.append((S, I, R))
    return out


def host_parasite(H0, P0, r=0.5, K=100, a=0.02, b=0.01, steps=2000, dt=0.05):
    H, P = H0, P0
    out = []
    for _ in range(steps):
        dH = r * H * (1 - H / K) - a * H * P
        dP = a * b * H * P - 0.5 * P
        H += dt * dH
        P += dt * dP
        out.append((H, P))
    return out


def predator_prey_spatial(n=32, steps=500, Du=0.1, Dv=0.1, seed=0):
    rng = random.Random(seed)
    u = [[0.5 + rng.random() * 0.1 for _ in range(n)] for _ in range(n)]
    v = [[0.3 + rng.random() * 0.1 for _ in range(n)] for _ in range(n)]
    for _ in range(steps):
        nu = [[0.0] * n for _ in range(n)]
        nv = [[0.0] * n for _ in range(n)]
        for y in range(1, n - 1):
            for x in range(1, n - 1):
                lu = u[y - 1][x] + u[y + 1][x] + u[y][x - 1] + u[y][x + 1] - 4 * u[y][x]
                lv = v[y - 1][x] + v[y + 1][x] + v[y][x - 1] + v[y][x + 1] - 4 * v[y][x]
                nu[y][x] = u[y][x] + Du * lu + u[y][x] * (1 - u[y][x]) - u[y][x] * v[y][x]
                nv[y][x] = v[y][x] + Dv * lv - 0.5 * v[y][x] + u[y][x] * v[y][x]
        u, v = nu, nv
    return {"u": u, "v": v}


@requirement(
    id="DCS-NAT-POP-001",
    title="logistic saturates at K",
    section="nature.population",
    hats=["DS", "SCI"],
    criticality="MUST",
)
def test_logistic():
    r = logistic(1.0, 1.0, 100.0, 4000)
    assert abs(r[-1] - 100.0) < 1.0


@requirement(
    id="DCS-NAT-POP-002",
    title="gompertz approaches its plateau",
    section="nature.population",
    hats=["DS", "SCI"],
    criticality="MUST",
)
def test_gompertz():
    r = gompertz(1.0, 0.5, 100.0, 3000)
    assert r[-1] > 20.0


@requirement(
    id="DCS-NAT-POP-003",
    title="Allee effect: below threshold → extinction",
    section="nature.population",
    hats=["SCI", "DS"],
    criticality="SHOULD",
)
def test_allee():
    low = allee(2.0, 1.0, 100.0, 5.0, 4000)
    high = allee(20.0, 1.0, 100.0, 5.0, 4000)
    assert low[-1] < high[-1]


@requirement(
    id="DCS-NAT-POP-004",
    title="Lotka-Volterra shows bounded cycles",
    section="nature.population",
    hats=["SCI", "QT"],
    criticality="SHOULD",
)
def test_lv():
    r = lotka_volterra(20, 5)
    xs = [p[0] for p in r]
    ys = [p[1] for p in r]
    assert max(xs) > min(xs) and max(ys) > min(ys)


@requirement(
    id="DCS-NAT-POP-005",
    title="SIR conserves total population",
    section="nature.population",
    hats=["DS", "SCI"],
    criticality="MUST",
)
def test_sir():
    r = sir(990, 10, 0)
    Ns = [S + I + R for S, I, R in r]
    assert max(Ns) - min(Ns) < 1.0


@requirement(
    id="DCS-NAT-POP-006",
    title="SIRS shows waning immunity (R re-enters S)",
    section="nature.population",
    hats=["DS", "SCI"],
    criticality="SHOULD",
)
def test_sirs():
    r = sirs(990, 10, 0)
    S_traj = [S for S, _, _ in r]
    assert S_traj[-1] > S_traj[len(S_traj) // 2]


@requirement(
    id="DCS-NAT-POP-007",
    title="host-parasite cycles (Red Queen)",
    section="nature.population",
    hats=["SCI", "QT"],
    criticality="SHOULD",
)
def test_hp():
    r = host_parasite(50, 5)
    Hs = [h for h, _ in r]
    Ps = [p for _, p in r]
    assert max(Hs) - min(Hs) > 1 and max(Ps) - min(Ps) > 1


@requirement(
    id="DCS-NAT-POP-008",
    title="spatial predator-prey forms patterns",
    section="nature.population",
    hats=["SCI", "SIM"],
    criticality="SHOULD",
)
def test_spatial():
    r = predator_prey_spatial(n=24, steps=200, seed=1)
    vals = [v for row in r["v"] for v in row]
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    assert var > 1e-4
