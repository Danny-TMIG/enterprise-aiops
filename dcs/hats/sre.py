"""SRE — sre. Error budget gate."""

from dcs.generate import requirement


def slo_ok(errors: int, total: int, budget: float = 0.01) -> bool:
    if total <= 0:
        return True
    return (errors / total) <= budget


@requirement(
    id="DCS-SRE-001",
    title="error budget enforced",
    section="SRE.sre",
    hats=["SRE"],
    criticality="MUST",
)
def test():
    assert slo_ok(0, 1000)
    assert slo_ok(1, 1000)  # 0.1% < 1%
    assert not slo_ok(20, 1000)
