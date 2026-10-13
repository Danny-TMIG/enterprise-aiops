"""Convergence validator for mesh subsystem probes."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class ConvergenceMetrics:
    achieved_value: float = 0.0
    expected: float = 1.0
    subsystem: str = "unknown"
    converged: bool = False
    attempts: int = 0
    elapsed_s: float = 0.0
    history: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "achieved_value": self.achieved_value,
            "expected": self.expected,
            "subsystem": self.subsystem,
            "converged": self.converged,
            "attempts": self.attempts,
            "elapsed_s": round(self.elapsed_s, 4),
            "history": [round(h, 6) for h in self.history],
        }


class MeshConvergenceValidator:
    def __init__(self, default_timeout: float = 5.0,
                 poll_interval: float = 0.05,
                 tolerance: float = 1e-9):
        self.default_timeout = float(default_timeout)
        self.poll_interval = float(poll_interval)
        self.tolerance = float(tolerance)

    async def assert_converges(self, probe_fn: Callable,
                                expected: float = 1.0,
                                subsystem: str = "unknown",
                                timeout: float | None = None
                                ) -> ConvergenceMetrics:
        t0 = time.time()
        deadline = t0 + (timeout if timeout is not None
                         else self.default_timeout)
        history: list = []
        attempts = 0
        value = 0.0
        while time.time() < deadline:
            attempts += 1
            try:
                v = probe_fn()
                if asyncio.iscoroutine(v):
                    v = await v
                value = float(v)
            except Exception:
                value = 0.0
            history.append(value)
            if abs(value - expected) <= self.tolerance:
                return ConvergenceMetrics(
                    achieved_value=value, expected=expected,
                    subsystem=subsystem, converged=True,
                    attempts=attempts, elapsed_s=time.time() - t0,
                    history=history,
                )
            await asyncio.sleep(self.poll_interval)
        return ConvergenceMetrics(
            achieved_value=value, expected=expected,
            subsystem=subsystem, converged=False,
            attempts=attempts, elapsed_s=time.time() - t0,
            history=history,
        )
