"""QT — quant. Monte-Carlo estimate of pi."""
import random
from dcs.generate import requirement

def mc_pi(n: int = 40_000, seed: int = 0) -> float:
    rng = random.Random(seed)
    hits = 0
    for _ in range(n):
        if rng.random()**2 + rng.random()**2 <= 1.0:
            hits += 1
    return 4.0 * hits / n

@requirement(id="DCS-QT-001", title="MC pi within 0.05 of math.pi",
             section="QT.quant", hats=["QT"], criticality="MUST")
def test():
    import math
    assert abs(mc_pi(40_000, seed=42) - math.pi) < 0.05

