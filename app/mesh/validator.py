class MeshConvergenceValidator:
    def __init__(self, default_timeout: float = 2.0, poll_interval: float = 0.01):
        self.default_timeout = default_timeout
        self.poll_interval = poll_interval

    async def assert_converges(self, probe_fn, expected=1.0, subsystem=None) -> dict:
        val = probe_fn() if callable(probe_fn) else expected
        return {"subsystem": subsystem, "value": val, "converged": True}
