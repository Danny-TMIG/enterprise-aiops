"""Prometheus metrics with a private registry.

Design constraints:

1. **Private registry.** Each ``Metrics`` instance owns a ``CollectorRegistry``.
   The global ``REGISTRY`` is not touched. Tests can create isolated instances.
2. **Bounded cardinality.** Labels are ``method``, ``path`` (route template),
   and ``status_class`` (1–5, or "0" for connection errors). Never the concrete
   URL, never the literal status code.
3. **Buckets sized for this workload.** Default histogram buckets target the
   10 ms – 5 s range typical of MLX inference and ledger writes.
4. **Fail open.** ``record`` swallows exceptions and logs at WARNING. A broken
   metric must never break a request.
5. **Async and sync.** ``track`` works for both. No coroutine-was-never-awaited.
"""
from __future__ import annotations

import time
import logging as _log
from contextlib import contextmanager
from typing import Any, Awaitable, Callable, Iterator, TypeVar

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

_logger = _log.getLogger("ag.metrics")

T = TypeVar("T")

# Buckets sized to the p50 (~80 ms) and p99 (seconds) of MLX inference.
# Two small buckets below 10 ms, dense coverage 10 ms – 5 s, two above.
DEFAULT_BUCKETS = (
    0.005, 0.010, 0.025, 0.050, 0.100, 0.250, 0.500,
    1.0, 2.5, 5.0, 10.0, 30.0,
)


class Metrics:
    """Per-process Prometheus instrument set with a private registry.

    Instantiate once per process (or once per test). All instruments live
    on ``self.registry`` and are exported by ``render()``.
    """

    def __init__(
        self,
        *,
        namespace: str = "sovereign",
        buckets: tuple[float, ...] = DEFAULT_BUCKETS,
        registry: CollectorRegistry | None = None,
    ) -> None:
        self.namespace = namespace
        self.buckets = buckets
        self.registry = registry if registry is not None else CollectorRegistry()

        self.requests = Counter(
            f"{namespace}_requests_total",
            "Total requests handled.",
            labelnames=("method", "path", "status_class"),
            registry=self.registry,
        )
        self.latency = Histogram(
            f"{namespace}_request_duration_seconds",
            "Request duration in seconds.",
            labelnames=("method", "path"),
            buckets=buckets,
            registry=self.registry,
        )
        self.in_flight = Gauge(
            f"{namespace}_requests_in_flight",
            "Number of requests currently being handled.",
            labelnames=("method", "path"),
            registry=self.registry,
        )
        self.errors = Counter(
            f"{namespace}_request_errors_total",
            "Total request errors (5xx and unhandled exceptions).",
            labelnames=("method", "path", "kind"),
            registry=self.registry,
        )

    # -----------------------------------------------------------------
    # Recording
    # -----------------------------------------------------------------
    def record(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_seconds: float,
    ) -> None:
        """Record one completed request. Never raises."""
        try:
            status_class = str(status_code // 100) if status_code > 0 else "0"
            self.requests.labels(method=method, path=path, status_class=status_class).inc()
            self.latency.labels(method=method, path=path).observe(duration_seconds)
            if status_class == "5":
                self.errors.labels(method=method, path=path, kind="5xx").inc()
        except Exception as e:  # noqa: BLE001
            _logger.warning("metrics record failed: %s", e)

    def record_exception(self, *, method: str, path: str, duration_seconds: float) -> None:
        """Record a request that raised before producing a status code."""
        try:
            self.requests.labels(method=method, path=path, status_class="0").inc()
            self.latency.labels(method=method, path=path).observe(duration_seconds)
            self.errors.labels(method=method, path=path, kind="exception").inc()
        except Exception as e:  # noqa: BLE001
            _logger.warning("metrics record_exception failed: %s", e)

    # -----------------------------------------------------------------
    # Context manager: wraps both sync and async call sites
    # -----------------------------------------------------------------
    @contextmanager
    def _timed(self, method: str, path: str) -> Iterator[dict[str, Any]]:
        start = time.perf_counter()
        state: dict[str, Any] = {"status": 0}
        self.in_flight.labels(method=method, path=path).inc()
        try:
            yield state
        finally:
            duration = time.perf_counter() - start
            self.in_flight.labels(method=method, path=path).dec()
            if state["status"] == 0:
                self.record_exception(method=method, path=path, duration_seconds=duration)
            else:
                self.record(
                    method=method,
                    path=path,
                    status_code=state["status"],
                    duration_seconds=duration,
                )

    def track(self, method: str, path: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator for sync handlers. The handler must set ``state['status']``.

        Example:
            @metrics.track("GET", "/items")
            def handler(state): state["status"] = 200
        """
        def decorator(fn: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args: Any, **kwargs: Any) -> T:
                with self._timed(method, path) as state:
                    return fn(*args, state=state, **kwargs)  # type: ignore[call-arg]
            return wrapper
        return decorator

    def track_async(
        self, method: str, path: str
    ) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
        """Decorator for async handlers. Awaits the inner coroutine."""
        def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                with self._timed(method, path) as state:
                    return await fn(*args, state=state, **kwargs)  # type: ignore[call-arg]
            return wrapper
        return decorator

    # -----------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------
    def render(self) -> bytes:
        """Return the current metric exposition in Prometheus text format."""
        return generate_latest(self.registry)

    @property
    def content_type(self) -> str:
        return CONTENT_TYPE_LATEST


# ---------------------------------------------------------------------------
# Process-wide default instance, lazily created.
# ---------------------------------------------------------------------------
_default: Metrics | None = None


def get_metrics() -> Metrics:
    """Return the process-wide Metrics instance, creating it on first call."""
    global _default
    if _default is None:
        _default = Metrics()
    return _default


def reset_default_metrics() -> None:
    """For tests. Drops the process-wide instance so a fresh one is created."""
    global _default
    _default = None
