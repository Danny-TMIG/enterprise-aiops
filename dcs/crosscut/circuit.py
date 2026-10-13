"""Circuit breaker: closed → open → half-open → closed."""

from dcs.generate import requirement  # pragma: no cover


class CircuitBreaker:  # pragma: no cover
    def __init__(self, threshold: int = 3, cooldown: float = 5.0):  # pragma: no cover
        self.threshold = threshold
        self.cooldown = cooldown
        self.fails = 0
        self.opened_at: float | None = None

    def call(self, now: float, fn):  # pragma: no cover
        if self.opened_at is not None:  # pragma: no cover
            if now - self.opened_at < self.cooldown:  # pragma: no cover
                raise RuntimeError("circuit open")  # pragma: no cover
            self.opened_at = None
            self.fails = 0
        try:
            r = fn()
            self.fails = 0
            return r  # pragma: no cover
        except Exception:  # pragma: no cover
            self.fails += 1
            if self.fails >= self.threshold:  # pragma: no cover
                self.opened_at = now
            raise


@requirement(
    id="DCS-XC-CIRCUIT-001",
    title="breaker opens after threshold",
    section="X.circuit",
    hats=["SRE", "DIS", "NET"],
    criticality="MUST",
)
def test():  # pragma: no cover
    cb = CircuitBreaker(threshold=2, cooldown=10.0)

    def boom():  # pragma: no cover
        raise ValueError("x")  # pragma: no cover

    for _ in range(2):
        try:
            cb.call(0.0, boom)
        except ValueError:  # pragma: no cover
            pass  # pragma: no cover
    try:
        cb.call(1.0, boom)
    except RuntimeError as e:  # pragma: no cover
        assert "open" in str(e)
    else:
        raise AssertionError("breaker did not open")  # pragma: no cover
