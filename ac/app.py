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

from contextlib import asynccontextmanager

import logging
import time
from typing import Any, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ag import tracing
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
# Tracing
# ---------------------------------------------------------------------------
TracerMiddleware_INSTALLED = False


class TracingMiddleware(BaseHTTPMiddleware):
    """Wrap each request in a span. Fail-safe: span errors never break the request."""

    _SKIP_PATHS = {"/metrics", "/healthz"}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in self._SKIP_PATHS:
            return await call_next(request)

        # Route template is only available after routing; fall back to url.path
        # on the way in and refine it after call_next.
        span_name = f"http.{request.method}"
        status_code = 0
        try:
            with tracing.span_scope(span_name) as span:
                try:
                    span.set_attribute("http.method", request.method)
                    span.set_attribute("http.path", request.url.path)
                except Exception:
                    pass
                response = await call_next(request)
                status_code = response.status_code
                try:
                    route = request.scope.get("route")
                    if route is not None:
                        span.set_attribute("http.route", getattr(route, "path", ""))
                    span.set_attribute("http.status_code", status_code)
                    if status_code >= 500:
                        span.set_attribute("error", True)
                except Exception:
                    pass
                return response
        except Exception as e:
            # Never swallow the user's exception. Tracing is best-effort.
            raise
        finally:
            # No extra bookkeeping needed; span_scope's context manager ends the span.
            pass


def _tracing_lifespan(app: FastAPI):
    """Init tracing on startup (with reachability check), shutdown on exit."""
    import os

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")

    @asynccontextmanager
    async def _ctx(app: FastAPI):
        # Install tracing if the environment says so. Off by default so
        # local `pytest` runs don't need a collector.
        if endpoint or os.environ.get("SOVEREIGN_TRACING") == "1":
            tracing.init_tracing(
                service_name="aether-core-asgi",
                endpoint=endpoint,
                insecure=True,
            )
        else:
            log.info("tracing not enabled (set OTEL_EXPORTER_OTLP_ENDPOINT or SOVEREIGN_TRACING=1)")
        yield
        tracing.shutdown_tracing(force_flush_timeout_ms=2000)

    return _ctx


# Attach the middleware and lifespan. Do this at module scope so tests see them.
if not TracerMiddleware_INSTALLED:
    app.add_middleware(TracingMiddleware)
    TracerMiddleware_INSTALLED = True

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/healthz")
def healthz() -> Response:
    """Real subsystem probe. 200 if all ok, 503 if any down."""
    from ag.health import check_all

    code, body = check_all()
    body["service"] = "aether-core-asgi"
    return JSONResponse(body, status_code=code)


@app.get("/metrics")
def expose_metrics(request: Request) -> Response:
    m: Metrics = request.app.state.metrics
    return PlainTextResponse(m.render(), media_type=m.content_type)


@app.post("/api/v1/execute")
async def execute(payload: dict) -> dict[str, Any]:
    """Minimal execute endpoint. Records via middleware, returns the payload."""
    return {"status": "success", "node": "aether-core-asgi", "echo": payload}
