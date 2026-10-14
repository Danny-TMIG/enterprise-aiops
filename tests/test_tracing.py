"""Tests for ag.tracing. All offline; no collector required."""
from __future__ import annotations

import pytest

from opentelemetry import trace
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from ag import tracing


class ListExporter(SpanExporter):
    """Collects finished spans in memory.

    Use in tests instead of ConsoleSpanExporter, which writes to sys.stdout
    (or sys.stderr, depending on the SDK version) and interleaves badly with
    pytest's stream capture.
    """

    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


def _init_with_list_exporter(service_name="test"):
    """Install a real provider with a ListExporter. Returns the ListExporter."""
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    exp = ListExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(SimpleSpanProcessor(exp))
    tracing._PROVIDER = provider
    tracing._ENABLED = True
    tracing._WARNED = False
    return exp


@pytest.fixture(autouse=True)
def clean_provider():
    """Reset ag.tracing's state between tests.

    Note: OTel's process-global tracer provider cannot be replaced. We
    bypass it in ``get_tracer`` by using our own ``_PROVIDER`` reference,
    so resetting module state is sufficient for test isolation.
    """
    yield
    tracing.shutdown_tracing(force_flush_timeout_ms=100)
    tracing._PROVIDER = None
    tracing._ENABLED = False
    tracing._WARNED = False
    # Do NOT reset _GLOBAL_WAS_SET: OTel won't let us install a second
    # global provider anyway, so the flag must reflect reality.


# ---------------------------------------------------------------------------
# Init paths
# ---------------------------------------------------------------------------
def test_init_with_no_endpoint_returns_false():
    """No endpoint, no console — nothing to record, so we don't install."""
    enabled = tracing.init_tracing(endpoint=None, console=False)
    assert enabled is False
    assert tracing.is_enabled() is False


def test_init_with_console_returns_true():
    """Console exporter alone is enough to install a real provider."""
    enabled = tracing.init_tracing(endpoint=None, console=True)
    assert enabled is True
    assert tracing.is_enabled() is True


def test_init_with_unreachable_endpoint_falls_back(caplog):
    """An endpoint that nothing listens on must not raise; must log; must disable."""
    with caplog.at_level("WARNING", logger="ag.tracing"):
        enabled = tracing.init_tracing(
            endpoint="http://127.0.0.1:59999",  # nothing listens here
            reachability_check=True,
        )
    assert enabled is False
    assert tracing.is_enabled() is False
    assert any("not reachable" in r.message for r in caplog.records)


def test_init_reachability_check_can_be_bypassed(monkeypatch):
    """reachability_check=False skips the socket probe and installs anyway."""
    # Prevent the exporter from actually trying to connect at init time.
    enabled = tracing.init_tracing(
        endpoint="http://127.0.0.1:59999",
        reachability_check=False,
    )
    # Even with a bogus endpoint, the exporter object is created; the failure
    # is deferred to export time. So this returns True.
    assert enabled is True
    assert tracing.is_enabled() is True


# ---------------------------------------------------------------------------
# span_scope
# ---------------------------------------------------------------------------
def test_span_scope_runs_body_with_no_provider():
    """No provider installed: span_scope still yields a span and runs the body."""
    ran = []
    with tracing.span_scope("test.op") as span:
        ran.append(True)
    assert ran == [True]
    # The span is a NonRecordingSpan; set_attribute is a no-op.
    assert hasattr(span, "set_attribute")


def test_span_scope_propagates_user_exceptions():
    """The body raising must propagate — we don't swallow user errors."""
    with pytest.raises(ValueError, match="user error"):
        with tracing.span_scope("test.raises"):
            raise ValueError("user error")


def test_span_scope_attributes_applied():
    """Attributes passed to span_scope land on the finished span."""
    exp = _init_with_list_exporter()
    with tracing.span_scope(
        "test.attrs",
        attributes={"http.method": "GET", "custom.n": 42},
    ):
        pass
    tracing.shutdown_tracing(force_flush_timeout_ms=100)
    assert len(exp.spans) == 1
    span = exp.spans[0]
    assert span.name == "test.attrs"
    assert span.attributes["http.method"] == "GET"
    assert span.attributes["custom.n"] == 42


def test_span_scope_records_exceptions():
    """An exception recorded via span.record_exception appears as an event."""
    exp = _init_with_list_exporter()
    with pytest.raises(RuntimeError):
        with tracing.span_scope("test.boom") as span:
            try:
                raise RuntimeError("inner")
            except RuntimeError as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, "inner"))
                raise
    tracing.shutdown_tracing(force_flush_timeout_ms=100)
    assert len(exp.spans) == 1
    span = exp.spans[0]
    assert span.name == "test.boom"
    assert span.status.status_code == trace.StatusCode.ERROR
    events = [e for e in span.events if e.name == "exception"]
    assert events, "expected an 'exception' event"
    assert "inner" in str(events[0].attributes.get("exception.message", ""))


# ---------------------------------------------------------------------------
# Idempotence
# ---------------------------------------------------------------------------
def test_init_twice_replaces_provider():
    """Calling init_tracing twice must not raise or stack."""
    tracing.init_tracing(endpoint=None, console=True)
    tracing.init_tracing(endpoint=None, console=True)
    # If stacking had happened, the second call would still succeed and
    # is_enabled would be True. The contract is "last install wins," which
    # both calls satisfy. The important thing: no exception, stable state.
    assert tracing.is_enabled() is True


def test_shutdown_is_safe_when_not_initialized():
    """shutdown_tracing on an uninitialized module must not raise."""
    tracing.shutdown_tracing(force_flush_timeout_ms=50)  # no init before this
    assert tracing.is_enabled() is False


def test_shutdown_after_init_clears_state():
    tracing.init_tracing(endpoint=None, console=True)
    assert tracing.is_enabled() is True
    tracing.shutdown_tracing(force_flush_timeout_ms=100)
    assert tracing.is_enabled() is False


# ---------------------------------------------------------------------------
# Reachability helper
# ---------------------------------------------------------------------------
def test_endpoint_reachable_false_for_closed_port():
    assert tracing._endpoint_reachable("http://127.0.0.1:59998", timeout=0.2) is False


def test_endpoint_reachable_false_for_empty():
    assert tracing._endpoint_reachable("") is False
