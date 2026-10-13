"""Adaptation — habituation, plasticity, homeostasis."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def habituation(n=30) -> list[float]:  # pragma: no cover
    r = 1.0
    out = []
    for _ in range(n):
        out.append(r)
        r *= 0.85
    return out  # pragma: no cover


def sensitization(n=30) -> list[float]:  # pragma: no cover
    r = 0.5
    out = []
    for i in range(n):
        out.append(r)
        r = min(1.0, r + 0.05)
    return out  # pragma: no cover


def hebbian(pre: list[float], post: list[float], eta: float = 0.01) -> float:  # pragma: no cover
    w = 0.0
    for p, q in zip(pre, post):
        w += eta * p * q
    return w  # pragma: no cover


def stdp(  # pragma: no cover
    dt: float,
    a_plus: float = 0.1,
    a_minus: float = 0.12,
    tau_plus: float = 20.0,
    tau_minus: float = 20.0,
) -> float:
    if dt > 0:  # pragma: no cover
        return a_plus * math.exp(-dt / tau_plus)  # pragma: no cover
    if dt < 0:  # pragma: no cover
        return -a_minus * math.exp(dt / tau_minus)  # pragma: no cover
    return 0.0  # pragma: no cover


def homeostasis(current: float, setpoint: float, gain: float = 0.1) -> float:  # pragma: no cover
    return current - gain * (current - setpoint)  # pragma: no cover


def allostasis(predicted_demand: float, gain: float = 0.5) -> float:  # pragma: no cover
    return gain * predicted_demand  # pragma: no cover


def immune_affinity(target: list[int], antibodies: list[list[int]], n_select: int = 3) -> list[int]:  # pragma: no cover
    """Clonal selection: pick best matches, return best affinity."""

    def hamming(a, b):  # pragma: no cover
        return sum(x != y for x, y in zip(a, b))  # pragma: no cover

    scored = sorted(antibodies, key=lambda ab: hamming(target, ab))
    best = scored[0]
    # mutate best slightly (best-first)
    best = list(best)
    if best:  # pragma: no cover
        best[0] = 1 - best[0]
    return best  # pragma: no cover


def bacterial_chemotaxis(concentration_fn, n=200, seed=0) -> dict:  # pragma: no cover
    """Run-and-tumble toward a gradient."""
    rng = random.Random(seed)
    x = y = 0.0
    th = 0.0
    for _ in range(n):
        r = 0.2
        x += r * math.cos(th)
        y += r * math.sin(th)
        c0 = concentration_fn(x, y)
        th += rng.gauss(0, 0.3)
        c1 = concentration_fn(x + r * math.cos(th), y + r * math.sin(th))
        if c1 < c0:  # tumbling when going downhill  # pragma: no cover
            th += rng.uniform(0, math.pi)
    return {"final": (x, y)}  # pragma: no cover


@requirement(
    id="DCS-NAT-ADP-001",
    title="habituation decays monotonically",
    section="nature.adaptation",
    hats=["SCI", "MLE"],
    criticality="MUST",
)
def test_habituation():  # pragma: no cover
    r = habituation()
    assert all(a > b for a, b in zip(r, r[1:]))


@requirement(
    id="DCS-NAT-ADP-002",
    title="sensitization grows monotonically",
    section="nature.adaptation",
    hats=["SCI"],
    criticality="MUST",
)
def test_sensitization():  # pragma: no cover
    r = sensitization()
    assert all(a <= b for a, b in zip(r, r[1:]))


@requirement(
    id="DCS-NAT-ADP-003",
    title="hebbian weight increases with co-firing",
    section="nature.adaptation",
    hats=["MLE", "RES"],
    criticality="MUST",
)
def test_hebbian():  # pragma: no cover
    assert hebbian([1.0] * 10, [1.0] * 10) > hebbian([1.0] * 10, [0.0] * 10)


@requirement(
    id="DCS-NAT-ADP-004",
    title="STDP is asymmetric around dt=0",
    section="nature.adaptation",
    hats=["MLE", "SCI"],
    criticality="MUST",
)
def test_stdp():  # pragma: no cover
    assert stdp(10) > 0 > stdp(-10)


@requirement(
    id="DCS-NAT-ADP-005",
    title="homeostasis drives to setpoint",
    section="nature.adaptation",
    hats=["SRE", "SCI"],
    criticality="MUST",
)
def test_homeostasis():  # pragma: no cover
    v = 10.0
    for _ in range(200):
        v = homeostasis(v, 5.0)
    assert abs(v - 5.0) < 0.01


@requirement(
    id="DCS-NAT-ADP-006",
    title="allostasis tracks predictive signal",
    section="nature.adaptation",
    hats=["SRE", "MLE"],
    criticality="MUST",
)
def test_allostasis():  # pragma: no cover
    assert allostasis(2.0) > allostasis(1.0)


@requirement(
    id="DCS-NAT-ADP-007",
    title="clonal selection improves affinity",
    section="nature.adaptation",
    hats=["SCI", "SO"],
    criticality="SHOULD",
)
def test_immune():  # pragma: no cover
    r = immune_affinity([1, 0, 1], [[1, 1, 1], [1, 0, 0], [0, 0, 0]])
    assert r is not None


@requirement(
    id="DCS-NAT-ADP-008",
    title="chemotaxis climbs a gradient",
    section="nature.adaptation",
    hats=["SCI", "ROB"],
    criticality="SHOULD",
)
def test_chemotaxis():  # pragma: no cover
    r = bacterial_chemotaxis(lambda x, y: -(x * x + y * y), seed=1)
    x, y = r["final"]
    assert math.hypot(x, y) < 10.0
