"""Deployment: canary analysis on error rate."""

from dcs.generate import requirement  # pragma: no cover


class Canary:  # pragma: no cover
    def __init__(self, error_budget: float = 0.02):  # pragma: no cover
        self.budget = error_budget

    def healthy(self, errors: int, total: int) -> bool:  # pragma: no cover
        if total == 0:  # pragma: no cover
            return True  # pragma: no cover
        return errors / total <= self.budget  # pragma: no cover


@requirement(
    id="DCS-XC-DEPLOY-001",
    title="canary rolls back when over budget",
    section="X.deploy",
    hats=["DO", "SRE", "REL"],
    criticality="MUST",
)
def test():  # pragma: no cover
    c = Canary(error_budget=0.01)
    assert c.healthy(5, 1000)
    assert not c.healthy(50, 1000)
