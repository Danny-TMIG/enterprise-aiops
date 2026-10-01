"""RES — research. Hypothesis threshold on improvement."""

from dcs.generate import requirement


def improved(baseline: float, candidate: float, delta: float = 0.02) -> bool:
    return (candidate - baseline) >= delta


@requirement(
    id="DCS-RES-001",
    title="improvement gate rejects noise",
    section="RES.research",
    hats=["RES"],
    criticality="MUST",
)
def test():
    assert improved(0.80, 0.85, 0.02)
    assert not improved(0.80, 0.81, 0.02)
