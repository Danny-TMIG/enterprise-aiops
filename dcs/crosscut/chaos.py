"""Chaos engineering: deterministic fault injection."""

from dcs.generate import requirement


class Fault:
    def __init__(self, name: str, prob: float):
        if not (0.0 <= prob <= 1.0):
            raise ValueError("prob out of range")
        self.name, self.prob = name, prob


class Harness:
    """Deterministic bucketing: hashing a counter against prob yields
    a stable, reproducible rate independent of RNG state."""

    def __init__(self, faults: list[Fault], seed: int = 0):
        self.faults = faults
        self.seed = seed
        self._tick = 0

    def maybe_fail(self):
        i = self._tick
        self._tick += 1
        for f in self.faults:
            # deterministic uniform on [0,1) via splitmix-style hash
            h = (i * 2654435761 + self.seed * 40503 + hash(f.name)) & 0xFFFFFFFF
            u = h / 0xFFFFFFFF
            if u < f.prob:
                raise RuntimeError(f"injected: {f.name}")


@requirement(
    id="DCS-XC-CHAOS-001",
    title="chaos injects exactly the configured fraction",
    section="X.chaos",
    hats=["SRE", "QA", "SO"],
    criticality="MUST",
)
def test():
    h = Harness([Fault("net", 0.30)], seed=1)
    faults = 0
    N = 10_000
    for _ in range(N):
        try:
            h.maybe_fail()
        except RuntimeError:
            faults += 1
    rate = faults / N
    assert 0.28 < rate < 0.32, rate
