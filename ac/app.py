"""ASGI control plane.

Real middleware, real metrics, no stubs. Every request is instrumented via
``ag.metrics``; the exposition is available at ``/metrics`` in Prometheus
text format.

Design notes:

- The middleware pulls ``path`` from ``request.scope["route"].path`` *after*
  routing, so label cardinality is bounded by the number of route templates,
  not the number of concrete URLs. Unmatched requests label as ``"unmatched"``.
- If metrics recording fails for any reason, the request is still served.
  Observability must never take down the request path.
- ``/metrics`` is itself excluded from instrumentation to avoid self-inflating
  scrape counters.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ag.metrics import Metrics

log = logging.getLogger("ac.app")

app = FastAPI(title="aether-core-asgi", version="0.1.0")

# One Metrics instance per process. Not the module-level default, so tests
# can wire their own by resetting ``app.state.metrics``.
metrics = Metrics(namespace="sovereign")
app.state.metrics = metrics


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
class MetricsMiddleware(BaseHTTPMiddleware):
    """Record every request. Fail open. Skip ``/metrics`` and ``/healthz``."""

    _SKIP_PATHS = {"/metrics", "/healthz"}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in self._SKIP_PATHS:
            return await call_next(request)

        m: Metrics = getattr(request.app.state, "metrics", None) or metrics
        start = time.perf_counter()
        status_code = 0
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            # record_exception handles the 0-status case
            raise
        finally:
            duration = time.perf_counter() - start
            # Route template: available after routing; fall back to "unmatched".
            route = request.scope.get("route")
            path = getattr(route, "path", None) or "unmatched"
            try:
                if status_code == 0:
                    m.record_exception(
                        method=request.method, path=path, duration_seconds=duration
                    )
                else:
                    m.record(
                        method=request.method,
                        path=path,
                        status_code=status_code,
                        duration_seconds=duration,
                    )
            except Exception as e:  # noqa: BLE001
                log.warning("metrics middleware failed: %s", e)


app.add_middleware(MetricsMiddleware)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return {"status": "ok", "service": "aether-core-asgi"}


@app.get("/metrics")
def expose_metrics(request: Request) -> Response:
    m: Metrics = request.app.state.metrics
    return PlainTextResponse(m.render(), media_type=m.content_type)


@app.post("/api/v1/execute")
async def execute(payload: dict) -> dict[str, Any]:
    """Minimal execute endpoint. Records via middleware, returns the payload."""
    return {"status": "success", "node": "aether-core-asgi", "echo": payload}
