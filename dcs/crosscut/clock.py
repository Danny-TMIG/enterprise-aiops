"""Clock: monotonic time + injectable clock for tests."""
import time
from dcs.generate import requirement

class Clock:
    def __init__(self, initial: float = 0.0):
        self._now = initial
    def now(self) -> float:
        return self._now
    def advance(self, dt: float) -> None:
        self._now += dt

def is_monotonic(seq) -> bool:
    return all(b >= a for a, b in zip(seq, seq[1:]))

@requirement(id="DCS-XC-CLOCK-001", title="injectable clock is monotonic",
             section="X.clock", hats=["SYS", "SIM"], criticality="MUST")
def test():
    c = Clock()
    stamps = []
    for _ in range(10):
        stamps.append(c.now()); c.advance(1.0)
    assert is_monotonic(stamps)
