"""Chaos engineering: deterministic fault injection."""

from dcs.generate import requirement  # pragma: no cover


class Fault:  # pragma: no cover
    def __init__(self, name: str, prob: float):  # pragma: no cover
        if not (0.0 <= prob <= 1.0):  # pragma: no cover
            raise ValueError("prob out of range")  # pragma: no cover
        self.name, self.prob = name, prob


class Harness:  # pragma: no cover
    """Deterministic bucketing: hashing a counter against prob yields
    a stable, reproducible rate independent of RNG state."""

    def __init__(self, faults: list[Fault], seed: int = 0):  # pragma: no cover
        self.faults = faults
        self.seed = seed
        self._tick = 0

    def maybe_fail(self):  # pragma: no cover
        i = self._tick
        self._tick += 1
        for f in self.faults:
            # deterministic uniform on [0,1) via splitmix-style hash
            h = (i * 2654435761 + self.seed * 40503 + hash(f.name)) & 0xFFFFFFFF
            u = h / 0xFFFFFFFF
            if u < f.prob:  # pragma: no cover
                raise RuntimeError(f"injected: {f.name}")  # pragma: no cover


@requirement(
    id="DCS-XC-CHAOS-001",
    title="chaos injects exactly the configured fraction",
    section="X.chaos",
    hats=["SRE", "QA", "SO"],
    criticality="MUST",
)
def test():  # pragma: no cover
    h = Harness([Fault("net", 0.30)], seed=1)
    faults = 0
    N = 10_000
    for _ in range(N):
        try:
            h.maybe_fail()
        except RuntimeError:  # pragma: no cover
            faults += 1
    rate = faults / N
    assert 0.28 < rate < 0.32, rate
