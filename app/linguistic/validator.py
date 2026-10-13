import asyncio
import time
from collections.abc import Callable
from typing import Any


class ConvergenceMetrics:
    def __init__(self, achieved_value: float, **kwargs: Any):
        self.achieved_value = achieved_value
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._data = {"achieved_value": achieved_value, **kwargs}

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class LinguisticValidator:
    def __init__(self, default_timeout: float = 2.0, poll_interval: float = 0.01):
        self.default_timeout = default_timeout
        self.poll_interval = poll_interval

    async def assert_converges(self, probe_fn: Callable[[], float], expected: float = 1.0, subsystem: str = "Linguistic") -> ConvergenceMetrics:
        start_time = time.time()
        while time.time() - start_time < self.default_timeout:
            val = probe_fn()
            if abs(float(val) - float(expected)) < 1e-5:
                return ConvergenceMetrics(achieved_value=float(val), converged=True, subsystem=subsystem)
            await asyncio.sleep(self.poll_interval)
        
        final_val = float(probe_fn())
        return ConvergenceMetrics(achieved_value=final_val, converged=False, subsystem=subsystem)
