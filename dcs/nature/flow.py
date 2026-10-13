"""Flow — transport, conduction, reactions at boundaries."""

import math  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def fick(C0, C1, D, x):  # pragma: no cover
    """Steady-state flux under Fick's first law."""
    return -D * (C1 - C0) / x  # pragma: no cover


def darcy(k, mu, dP, L):  # pragma: no cover
    return -k / mu * dP / L  # pragma: no cover


def poiseuille(r, mu, dP, L):  # pragma: no cover
    return math.pi * r**4 * dP / (8 * mu * L)  # pragma: no cover


def kirchhoff(flows_in: list[float], flows_out: list[float]) -> bool:  # pragma: no cover
    return abs(sum(flows_in) - sum(flows_out)) < 1e-9  # pragma: no cover


def fourier(k, dT, x):  # pragma: no cover
    return -k * dT / x  # pragma: no cover


def nernst(z, T=310.0, R=8.314, F=96485.0, c_in=10.0, c_out=1.0) -> float:  # pragma: no cover
    """Nernst equilibrium potential (mV)."""
    return (R * T) / (z * F) * math.log(c_out / c_in) * 1000.0  # pragma: no cover


def chemostat(S0, X0, mu_max=1.0, Ks=1.0, D=0.5, steps=2000, dt=0.01):  # pragma: no cover
    """Monod chemostat: dilution D."""
    S, X = S0, X0
    out = []
    for _ in range(steps):
        mu = mu_max * S / (Ks + S)
        dS = D * (1.0 - S) - mu * X
        dX = (mu - D) * X
        S += dt * dS
        X += dt * dX
        S = max(0, S)
        X = max(0, X)
        out.append((S, X))
    return out  # pragma: no cover


def osmosis(concentration_difference, membrane_permeability=1.0) -> float:  # pragma: no cover
    """Flux proportional to concentration difference."""
    return membrane_permeability * concentration_difference  # pragma: no cover


def diffusion_limited_reaction(k_rxn, D, C_bulk, delta):  # pragma: no cover
    """Flux into a boundary where reaction is instantaneous (Smoluchowski)."""
    return -D * (0.0 - C_bulk) / delta  # pragma: no cover


@requirement(
    id="DCS-NAT-FLOW-001",
    title="Fick flux scales with concentration gradient",
    section="nature.flow",
    hats=["SCI", "HPC"],
    criticality="MUST",
)
def test_fick():  # pragma: no cover
    assert abs(fick(10, 0, 1, 1) - 10) < 1e-9


@requirement(
    id="DCS-NAT-FLOW-002",
    title="Darcy flow scales with pressure gradient",
    section="nature.flow",
    hats=["SCI"],
    criticality="MUST",
)
def test_darcy():  # pragma: no cover
    assert darcy(1.0, 1.0, -2.0, 1.0) == 2.0


@requirement(
    id="DCS-NAT-FLOW-003",
    title="Poiseuille flow ∝ r⁴",
    section="nature.flow",
    hats=["SCI", "HPC"],
    criticality="MUST",
)
def test_poiseuille():  # pragma: no cover
    q1 = poiseuille(1.0, 1.0, 1.0, 1.0)
    q2 = poiseuille(2.0, 1.0, 1.0, 1.0)
    assert abs(q2 / q1 - 16.0) < 1e-9


@requirement(
    id="DCS-NAT-FLOW-004",
    title="Kirchhoff: in = out",
    section="nature.flow",
    hats=["NET", "SYS"],
    criticality="MUST",
)
def test_kirchhoff():  # pragma: no cover
    assert kirchhoff([1, 2, 3], [2, 4])
    assert not kirchhoff([1, 2, 3], [2, 3])


@requirement(
    id="DCS-NAT-FLOW-005",
    title="Fourier heat flux with negative gradient",
    section="nature.flow",
    hats=["SCI"],
    criticality="MUST",
)
def test_fourier():  # pragma: no cover
    assert fourier(1, -5, 1) == 5


@requirement(
    id="DCS-NAT-FLOW-006",
    title="Nernst potential for K+ is negative inside",
    section="nature.flow",
    hats=["SCI", "RES"],
    criticality="MUST",
)
def test_nernst():  # pragma: no cover
    # For a positive ion with higher concentration inside, E is negative
    E = nernst(z=1, c_in=100, c_out=5)
    assert E < 0


@requirement(
    id="DCS-NAT-FLOW-007",
    title="chemostat reaches steady state",
    section="nature.flow",
    hats=["SCI", "DB"],
    criticality="MUST",
)
def test_chemostat():  # pragma: no cover
    r = chemostat(1.0, 0.05)
    S_last = r[-1][0]
    X_last = r[-1][1]
    S_prev = r[-100][0]
    X_prev = r[-100][1]
    assert abs(S_last - S_prev) < 1e-3 and abs(X_last - X_prev) < 1e-3


@requirement(
    id="DCS-NAT-FLOW-008",
    title="osmosis driven by concentration difference",
    section="nature.flow",
    hats=["SCI", "EMB"],
    criticality="MUST",
)
def test_osmosis():  # pragma: no cover
    assert osmosis(2.0) > 0 and osmosis(-1.0) < 0


@requirement(
    id="DCS-NAT-FLOW-009",
    title="diffusion-limited flux scales with 1/δ",
    section="nature.flow",
    hats=["SCI"],
    criticality="MUST",
)
def test_diffusion_limited():  # pragma: no cover
    a = diffusion_limited_reaction(1, 1, 1, 1)
    b = diffusion_limited_reaction(1, 1, 1, 2)
    assert abs(a / b - 2.0) < 1e-9
