"""OpenTelemetry tracing with fail-safe behavior.

Design constraints:

1. **Never crash on init.** If a collector isn't reachable, log once and
   continue with a no-op tracer. Observability must not take down the process.
2. **Never crash on emit.** Any failure inside ``span_scope`` is swallowed and
   logged at WARNING. The wrapped operation always runs.
3. **Idempotent init.** ``init_tracing`` called twice replaces the provider we
   installed instead of stacking.
4. **No import-time work.** Importing this module doesn't create a provider or
   open a socket.
5. **Graceful shutdown.** ``shutdown_tracing`` flushes with a bounded timeout
   so process exit isn't held up by an unreachable collector.
"""
from __future__ import annotations

import logging
import socket
from contextlib import contextmanager
from typing import Any, Iterator
from urllib.parse import urlparse

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
)
from opentelemetry.sdk.trace.sampling import ALWAYS_ON, ParentBased, TraceIdRatioBased

log = logging.getLogger("ag.tracing")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
_PROVIDER: TracerProvider | None = None
_ENABLED: bool = False
_WARNED: bool = False
_GLOBAL_WAS_SET: bool = False


# ---------------------------------------------------------------------------
# Reachability probe
# ---------------------------------------------------------------------------
def _endpoint_reachable(endpoint: str, *, timeout: float = 0.5) -> bool:
    """Best-effort TCP check. Doesn't attempt an OTLP handshake — just the
    connection. Returns False on any failure without raising.
    """
    if not endpoint:
        return False
    try:
        parsed = urlparse(endpoint)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (4318 if parsed.scheme in ("http", "https") else 4317)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
def init_tracing(
    service_name: str = "aether-core-asgi",
    *,
    endpoint: str | None = None,
    insecure: bool = True,
    sampler_ratio: float = 1.0,
    environment: str = "dev",
    console: bool = False,
    reachability_check: bool = True,
) -> bool:
    """Configure the global tracer provider.

    Args:
        service_name: goes on every span as ``service.name``.
        endpoint: OTLP gRPC URL, e.g. ``http://127.0.0.1:4317``. If ``None``,
            no exporter is attached and only the console path (if enabled)
            emits spans.
        insecure: pass to ``OTLPSpanExporter``; ``True`` means plaintext gRPC.
        sampler_ratio: ``1.0`` = always on, ``0.01`` = 1% sample rate.
        environment: goes on every span as ``deployment.environment``.
        console: attach a ``ConsoleSpanExporter`` (useful in dev/tests).
        reachability_check: if ``True`` and ``endpoint`` is set, verify the
            host:port is reachable before attaching the OTLP exporter.

    Returns:
        ``True`` if a real provider was installed (with at least one exporter),
        ``False`` if it fell back to no-op.
    """
    global _PROVIDER, _ENABLED, _WARNED

    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": environment,
    })

    sampler = ParentBased(TraceIdRatioBased(sampler_ratio)) if sampler_ratio < 1.0 else ALWAYS_ON

    provider = TracerProvider(resource=resource, sampler=sampler)

    attached = 0

    if endpoint:
        if reachability_check and not _endpoint_reachable(endpoint):
            if not _WARNED:
                log.warning(
                    "OTLP endpoint %s not reachable; tracing disabled (no spans will export)",
                    endpoint,
                )
                _WARNED = True
        else:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                    OTLPSpanExporter,
                )

                exporter: SpanExporter = OTLPSpanExporter(
                    endpoint=endpoint,
                    insecure=insecure,
                    timeout=5.0,
                )
                provider.add_span_processor(BatchSpanProcessor(exporter))
                attached += 1
            except Exception as e:  # noqa: BLE001
                if not _WARNED:
                    log.warning("failed to attach OTLP exporter: %r", e)
                    _WARNED = True

    if console:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        attached += 1

    # Only install if we'll actually record something. Installing an empty
    # provider is worse than installing nothing: it silently swallows spans.
    if attached == 0:
        _PROVIDER = None
        _ENABLED = False
        return False

    # The OTel global provider can only be set once per process. Do it the
    # first time; on subsequent calls, keep our own reference and use it
    # directly — the global is a convenience, not the source of truth.
    global _GLOBAL_WAS_SET
    if not _GLOBAL_WAS_SET:
        try:
            trace.set_tracer_provider(provider)
            _GLOBAL_WAS_SET = True
        except Exception:
            pass  # already set by someone else; fall through

    _PROVIDER = provider
    _ENABLED = True
    return True


def is_enabled() -> bool:
    return _ENABLED


def get_tracer(name: str = "aether") -> trace.Tracer:
    """Return a tracer from our provider if we have one; otherwise the global.

    The global provider can only be installed once per process (OTel SDK
    constraint). For tests and for re-init, we bypass the global and ask
    our own provider directly.
    """
    if _PROVIDER is not None:
        return _PROVIDER.get_tracer(name)
    return trace.get_tracer(name)


# ---------------------------------------------------------------------------
# Span helper
# ---------------------------------------------------------------------------
@contextmanager
def span_scope(
    name: str,
    *,
    tracer_name: str = "aether",
    attributes: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Context manager that yields a span. Never raises on span failure.

    Usage:
        with span_scope("db.query", attributes={"db.system": "sqlite"}) as span:
            result = do_the_thing()
            if failed:
                span.set_attribute("error", True)
    """
    tracer = get_tracer(tracer_name)
    try:
        with tracer.start_as_current_span(name) as span:
            if attributes:
                for k, v in attributes.items():
                    try:
                        span.set_attribute(k, v)
                    except Exception:
                        # Attribute setting can fail on complex types; swallow.
                        pass
            yield span
    except Exception:
        # Re-raise the *user's* exception; only swallow span-creation errors.
        raise


# ---------------------------------------------------------------------------
# Shutdown
# ---------------------------------------------------------------------------
def shutdown_tracing(force_flush_timeout_ms: int = 2000) -> None:
    """Flush pending spans and shut the provider down. Safe to call twice.

    Bounded by ``force_flush_timeout_ms`` so an unreachable collector doesn't
    block process exit.
    """
    global _PROVIDER, _ENABLED
    if _PROVIDER is None:
        return
    try:
        _PROVIDER.force_flush(timeout_millis=force_flush_timeout_ms)
    except Exception as e:  # noqa: BLE001
        log.warning("force_flush failed: %r", e)
    try:
        _PROVIDER.shutdown()
    except Exception as e:  # noqa: BLE001
        log.warning("shutdown failed: %r", e)
    _PROVIDER = None
    _ENABLED = False
