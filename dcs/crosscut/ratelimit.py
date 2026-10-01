"""Rate limiting: token bucket."""
from dcs.generate import requirement

class TokenBucket:
    def __init__(self, rate: float, burst: int):
        self.rate = rate; self.burst = burst
        self.tokens = float(burst); self.last = 0.0
    def allow(self, now: float, n: int = 1) -> bool:
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= n:
            self.tokens -= n; return True
        return False

@requirement(id="DCS-XC-RATE-001", title="token bucket enforces burst then rate",
             section="X.ratelimit", hats=["NET", "NWE", "SRE"], criticality="MUST")
def test():
    b = TokenBucket(rate=10.0, burst=5)
    assert sum(b.allow(0.0) for _ in range(10)) == 5    # burst exhausted
    assert b.allow(1.0) is True                          # 10 refilled
