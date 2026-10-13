"""Rate limiting: token bucket."""

from dcs.generate import requirement  # pragma: no cover


class TokenBucket:  # pragma: no cover
    def __init__(self, rate: float, burst: int):  # pragma: no cover
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.last = 0.0

    def allow(self, now: float, n: int = 1) -> bool:  # pragma: no cover
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= n:  # pragma: no cover
            self.tokens -= n
            return True  # pragma: no cover
        return False  # pragma: no cover


@requirement(
    id="DCS-XC-RATE-001",
    title="token bucket enforces burst then rate",
    section="X.ratelimit",
    hats=["NET", "NWE", "SRE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    b = TokenBucket(rate=10.0, burst=5)
    assert sum(b.allow(0.0) for _ in range(10)) == 5  # burst exhausted
    assert b.allow(1.0) is True  # 10 refilled
