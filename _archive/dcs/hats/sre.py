"""SRE — sre. Error budget gate."""

from dcs.generate import requirement  # pragma: no cover


def slo_ok(errors: int, total: int, budget: float = 0.01) -> bool:  # pragma: no cover
    if total <= 0:  # pragma: no cover
        return True  # pragma: no cover
    return (errors / total) <= budget  # pragma: no cover


@requirement(
    id="DCS-SRE-001",
    title="error budget enforced",
    section="SRE.sre",
    hats=["SRE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert slo_ok(0, 1000)
    assert slo_ok(1, 1000)  # 0.1% < 1%
    assert not slo_ok(20, 1000)
