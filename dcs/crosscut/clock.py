"""Clock: monotonic time + injectable clock for tests."""

from dcs.generate import requirement  # pragma: no cover


class Clock:  # pragma: no cover
    def __init__(self, initial: float = 0.0):  # pragma: no cover
        self._now = initial

    def now(self) -> float:  # pragma: no cover
        return self._now  # pragma: no cover

    def advance(self, dt: float) -> None:  # pragma: no cover
        self._now += dt


def is_monotonic(seq) -> bool:  # pragma: no cover
    return all(b >= a for a, b in zip(seq, seq[1:]))  # pragma: no cover


@requirement(
    id="DCS-XC-CLOCK-001",
    title="injectable clock is monotonic",
    section="X.clock",
    hats=["SYS", "SIM"],
    criticality="MUST",
)
def test():  # pragma: no cover
    c = Clock()
    stamps = []
    for _ in range(10):
        stamps.append(c.now())
        c.advance(1.0)
    assert is_monotonic(stamps)
