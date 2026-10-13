"""QT — quant. Monte-Carlo estimate of pi."""

import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def mc_pi(n: int = 40_000, seed: int = 0) -> float:  # pragma: no cover
    rng = random.Random(seed)
    hits = 0
    for _ in range(n):
        if rng.random() ** 2 + rng.random() ** 2 <= 1.0:  # pragma: no cover
            hits += 1
    return 4.0 * hits / n  # pragma: no cover


@requirement(
    id="DCS-QT-001",
    title="MC pi within 0.05 of math.pi",
    section="QT.quant",
    hats=["QT"],
    criticality="MUST",
)
def test():  # pragma: no cover
    import math  # pragma: no cover

    assert abs(mc_pi(40_000, seed=42) - math.pi) < 0.05
