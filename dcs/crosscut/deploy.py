"""Deployment: canary analysis on error rate."""
from dcs.generate import requirement

class Canary:
    def __init__(self, error_budget: float = 0.02):
        self.budget = error_budget
    def healthy(self, errors: int, total: int) -> bool:
        if total == 0: return True
        return errors / total <= self.budget

@requirement(id="DCS-XC-DEPLOY-001", title="canary rolls back when over budget",
             section="X.deploy", hats=["DO", "SRE", "REL"], criticality="MUST")
def test():
    c = Canary(error_budget=0.01)
    assert c.healthy(5, 1000)
    assert not c.healthy(50, 1000)
