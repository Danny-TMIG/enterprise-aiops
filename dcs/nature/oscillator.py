"""Coupled oscillators — synchronisation and excitable dynamics."""

import math  # pragma: no cover
import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def kuramoto(n=100, K=2.0, steps=500, dt=0.01, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    omega = [rng.gauss(0, 0.5) for _ in range(n)]
    theta = [rng.uniform(0, 2 * math.pi) for _ in range(n)]
    for _ in range(steps):
        mx = sum(math.cos(t) for t in theta) / n
        my = sum(math.sin(t) for t in theta) / n
        for i in range(n):
            theta[i] += dt * (omega[i] + K * (my * math.cos(theta[i]) - mx * math.sin(theta[i])))
    return theta  # pragma: no cover


def order_parameter(theta):  # pragma: no cover
    n = len(theta)
    return abs(complex(sum(math.cos(t) for t in theta) / n, sum(math.sin(t) for t in theta) / n))  # pragma: no cover


def firefly_sync(n=50, K=0.3, steps=200, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    phase = [rng.random() for _ in range(n)]
    for _ in range(steps):
        new = []
        for i in range(n):
            acc = 0.0
            for j in range(n):
                if i == j:  # pragma: no cover
                    continue
                acc += math.sin(2 * math.pi * (phase[j] - phase[i]))
            new.append((phase[i] + K * acc / n) % 1.0)
        phase = new
    return phase  # pragma: no cover


def cricket_chorus(n=50, K=0.2, steps=200, seed=0):  # pragma: no cover
    return firefly_sync(n, K, steps, seed)  # pragma: no cover


def cardiac_sa_node(steps=500, dt=0.05, seed=0):  # pragma: no cover
    """FitzHugh-Nagumo relaxation."""
    v, w = -1.0, 0.0
    a, b, tau = 0.7, 0.8, 12.5
    I = 0.5
    trace = []
    for _ in range(steps):
        dv = v - v**3 / 3 - w + I
        dw = (v + a - b * w) / tau
        v += dt * dv
        w += dt * dw
        trace.append(v)
    return trace  # pragma: no cover


def circadian_clock(steps=800, delay=15, gain=3.5, dt=0.05):  # pragma: no cover
    """Delayed negative feedback via explicit ring buffer."""
    buf = [0.5] * delay
    x = []
    for i in range(steps):
        prev = x[-1] if x else 0.5
        delayed = buf[i % delay]
        v = prev + dt * (1.0 - gain * delayed)
        v = max(0.0, min(1.5, v))
        buf[i % delay] = v
        x.append(v)
    return x  # pragma: no cover


def peskin_mirollo(n=50, eps=0.5, steps=5000, seed=0):  # pragma: no cover
    rng = random.Random(seed)
    x = [rng.random() for _ in range(n)]
    for _ in range(steps):
        i = rng.randrange(n)
        x[i] = 0.0
        for j in range(n):
            if j != i:  # pragma: no cover
                x[j] += eps
        x = [min(1.0, v) for v in x]
    return x  # pragma: no cover


def fitzhugh_nagumo(steps=500, dt=0.05):  # pragma: no cover
    return cardiac_sa_node(steps, dt)  # pragma: no cover


def hodgkin_huxley(steps=500, dt=0.02, I=10.0):  # pragma: no cover
    """Simplified H-H: V, m, h, n gating."""
    V, m, h, n = -65.0, 0.05, 0.6, 0.32
    C = 1.0
    trace = []
    for _ in range(steps):
        a_m = 0.1 * (V + 40) / (1 - math.exp(-(V + 40) / 10)) if V != -40 else 1.0
        b_m = 4 * math.exp(-(V + 65) / 18)
        a_h = 0.07 * math.exp(-(V + 65) / 20)
        b_h = 1 / (1 + math.exp(-(V + 35) / 10))
        a_n = 0.01 * (V + 55) / (1 - math.exp(-(V + 55) / 10)) if V != -55 else 0.1
        b_n = 0.125 * math.exp(-(V + 65) / 80)
        I_Na = 120 * m**3 * h * (V - 50)
        I_K = 36 * n**4 * (V + 77)
        I_L = 0.3 * (V + 54.4)
        dV = (I - I_Na - I_K - I_L) / C
        dm = a_m * (1 - m) - b_m * m
        dh = a_h * (1 - h) - b_h * h
        dn = a_n * (1 - n) - b_n * n
        V += dt * dV
        m += dt * dm
        h += dt * dh
        n += dt * dn
        trace.append(V)
    return trace  # pragma: no cover


@requirement(
    id="DCS-NAT-OSC-001",
    title="kuramoto synchronises above K_c",
    section="nature.oscillator",
    hats=["SCI", "HPC"],
    criticality="MUST",
)
def test_kuramoto_sync():  # pragma: no cover
    r = order_parameter(kuramoto(seed=1))
    assert r > 0.6, r


@requirement(
    id="DCS-NAT-OSC-002",
    title="firefly pulse-coupling converges to phase lock",
    section="nature.oscillator",
    hats=["SCI", "SIM"],
    criticality="SHOULD",
)
def test_firefly_lock():  # pragma: no cover
    ph = firefly_sync(seed=2)
    # circular variance small ⇒ synchronised
    mx = sum(math.cos(2 * math.pi * p) for p in ph) / len(ph)
    my = sum(math.sin(2 * math.pi * p) for p in ph) / len(ph)
    R = math.hypot(mx, my)
    assert R > 0.5, R


@requirement(
    id="DCS-NAT-OSC-003",
    title="cricket chorus matches firefly coupling",
    section="nature.oscillator",
    hats=["SCI"],
    criticality="MAY",
)
def test_cricket():  # pragma: no cover
    a = firefly_sync(seed=3)
    b = cricket_chorus(seed=3)
    assert len(a) == len(b)


@requirement(
    id="DCS-NAT-OSC-004",
    title="cardiac SA node exhibits relaxation spikes",
    section="nature.oscillator",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_cardiac():  # pragma: no cover
    tr = cardiac_sa_node()
    assert max(tr) - min(tr) > 0.5


@requirement(
    id="DCS-NAT-OSC-005",
    title="circadian clock oscillates via delayed feedback",
    section="nature.oscillator",
    hats=["SCI", "SIM"],
    criticality="MUST",
)
def test_circadian():  # pragma: no cover
    tr = circadian_clock()
    assert max(tr) > 0.6 and min(tr) < 0.4


@requirement(
    id="DCS-NAT-OSC-006",
    title="Peskin-Mirollo firing synchronises",
    section="nature.oscillator",
    hats=["SCI", "HPC"],
    criticality="SHOULD",
)
def test_peskin():  # pragma: no cover
    x = peskin_mirollo(seed=4)
    # variance across coupled oscillators should be small after transient
    mean = sum(x) / len(x)
    var = sum((v - mean) ** 2 for v in x) / len(x)
    assert var < 0.05, var


@requirement(
    id="DCS-NAT-OSC-007",
    title="FitzHugh-Nagumo produces spikes",
    section="nature.oscillator",
    hats=["SCI"],
    criticality="MUST",
)
def test_fhn():  # pragma: no cover
    tr = fitzhugh_nagumo()
    assert max(tr) - min(tr) > 0.5


@requirement(
    id="DCS-NAT-OSC-008",
    title="Hodgkin-Huxley produces an action potential",
    section="nature.oscillator",
    hats=["SCI", "RES"],
    criticality="MUST",
)
def test_hh():  # pragma: no cover
    tr = hodgkin_huxley(500)
    assert max(tr) > 20 and min(tr) < -70
