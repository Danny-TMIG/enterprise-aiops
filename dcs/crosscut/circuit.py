"""Circuit breaker: closed → open → half-open → closed."""

from dcs.generate import requirement


class CircuitBreaker:
    def __init__(self, threshold: int = 3, cooldown: float = 5.0):
        self.threshold = threshold
        self.cooldown = cooldown
        self.fails = 0
        self.opened_at: float | None = None

    def call(self, now: float, fn):
        if self.opened_at is not None:
            if now - self.opened_at < self.cooldown:
                raise RuntimeError("circuit open")
            self.opened_at = None
            self.fails = 0
        try:
            r = fn()
            self.fails = 0
            return r
        except Exception:
            self.fails += 1
            if self.fails >= self.threshold:
                self.opened_at = now
            raise


@requirement(
    id="DCS-XC-CIRCUIT-001",
    title="breaker opens after threshold",
    section="X.circuit",
    hats=["SRE", "DIS", "NET"],
    criticality="MUST",
)
def test():
    cb = CircuitBreaker(threshold=2, cooldown=10.0)

    def boom():
        raise ValueError("x")

    for _ in range(2):
        try:
            cb.call(0.0, boom)
        except ValueError:
            pass
    try:
        cb.call(1.0, boom)
    except RuntimeError as e:
        assert "open" in str(e)
    else:
        raise AssertionError("breaker did not open")
