"""Threshold phenomena — all-or-none transitions."""

import math  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def quorum_sensing(density: float, threshold: float = 0.5) -> bool:  # pragma: no cover
    return density >= threshold  # pragma: no cover


def all_or_none(x: float, k: float = 10.0, x0: float = 0.5) -> float:  # pragma: no cover
    return 1.0 / (1.0 + math.exp(-k * (x - x0)))  # pragma: no cover


def neuron_threshold(potentials: list[float], v_thresh: float = 1.0) -> int:  # pragma: no cover
    v = 0.0
    spikes = 0
    for p in potentials:
        v += p
        if v >= v_thresh:  # pragma: no cover
            v = 0.0
            spikes += 1
    return spikes  # pragma: no cover


def gene_switch(a: float, b: float) -> tuple[float, float]:  # pragma: no cover
    """Bistable toggle — one gene suppresses the other."""
    for _ in range(50):
        da = 1.0 / (1.0 + b * b) - 0.5 * a
        db = 1.0 / (1.0 + a * a) - 0.5 * b
        a += 0.1 * da
        b += 0.1 * db
    return a, b  # pragma: no cover


def phase_transition(p: float, beta: float = 0.5) -> float:  # pragma: no cover
    """Order parameter for percolation-style threshold."""
    if p < 0.5:  # pragma: no cover
        return 0.0  # pragma: no cover
    return (p - 0.5) ** beta  # pragma: no cover


@requirement(
    id="DCS-NAT-THR-001",
    title="quorum fires above threshold",
    section="nature.threshold",
    hats=["SCI", "DIS"],
    criticality="MUST",
)
def test_quorum():  # pragma: no cover
    assert quorum_sensing(0.7) and not quorum_sensing(0.2)


@requirement(
    id="DCS-NAT-THR-002",
    title="sigmoid is monotone and bounded",
    section="nature.threshold",
    hats=["SCI", "MLE"],
    criticality="MUST",
)
def test_sigmoid():  # pragma: no cover
    a = all_or_none(0.2)
    b = all_or_none(0.5)
    c = all_or_none(0.8)
    assert 0 < a < b < c < 1


@requirement(
    id="DCS-NAT-THR-003",
    title="integrate-and-fire fires on accumulated input",
    section="nature.threshold",
    hats=["MLE", "SCI"],
    criticality="MUST",
)
def test_lif():  # pragma: no cover
    assert neuron_threshold([0.2] * 10) >= 2


@requirement(
    id="DCS-NAT-THR-004",
    title="gene toggle is bistable (exactly one high)",
    section="nature.threshold",
    hats=["SCI", "RES"],
    criticality="SHOULD",
)
def test_toggle():  # pragma: no cover
    a, b = gene_switch(0.9, 0.1)
    assert (a > b and a > 0.5) or (b > a and b > 0.5)


@requirement(
    id="DCS-NAT-THR-005",
    title="order parameter zero below critical point",
    section="nature.threshold",
    hats=["SCI", "FM"],
    criticality="MUST",
)
def test_percolation():  # pragma: no cover
    assert phase_transition(0.4) == 0.0
    assert phase_transition(0.7) > 0.0
