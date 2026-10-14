"""Tests that ac.app actually emits spans per request.

Uses the same ListExporter pattern as tests/test_tracing.py — deterministic,
no network, no reliance on stream capture.
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

from ac.app import app


class ListExporter(SpanExporter):
    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


@pytest.fixture
def client_and_exporter():
    """Fresh ListExporter + provider per test so spans don't leak across tests."""
    from ag import tracing
    from ag.metrics import Metrics
    from ag.settings import reset_settings_cache

    exp = ListExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "ac-test"}))
    provider.add_span_processor(SimpleSpanProcessor(exp))

    old_provider = tracing._PROVIDER
    old_enabled = tracing._ENABLED
    tracing._PROVIDER = provider
    tracing._ENABLED = True

    app.state.metrics = Metrics(namespace="sovereign")

    os.environ["SOVEREIGN_NODE_ID"] = "test-node"
    reset_settings_cache()

    with TestClient(app) as c:
        yield c, exp

    tracing._PROVIDER = old_provider
    tracing._ENABLED = old_enabled
    tracing.shutdown_tracing(force_flush_timeout_ms=100)
    tracing._PROVIDER = None
    tracing._ENABLED = False
    reset_settings_cache()


def _by_name(exp, prefix):
    return [s for s in exp.spans if s.name.startswith(prefix)]


def test_post_execute_emits_one_span(client_and_exporter):
    client, exp = client_and_exporter
    r = client.post("/api/v1/execute", json={"a": 1})
    assert r.status_code == 200
    spans = _by_name(exp, "http.POST")
    assert len(spans) == 1, f"expected 1 span, got {[s.name for s in exp.spans]}"
    span = spans[0]
    assert span.attributes["http.method"] == "POST"
    assert span.attributes["http.path"] == "/api/v1/execute"
    assert span.attributes["http.route"] == "/api/v1/execute"
    assert span.attributes["http.status_code"] == 200


def test_get_healthz_is_not_traced(client_and_exporter):
    client, exp = client_and_exporter
    client.get("/healthz")
    assert _by_name(exp, "http.GET") == []


def test_get_metrics_is_not_traced(client_and_exporter):
    client, exp = client_and_exporter
    client.get("/metrics")
    assert _by_name(exp, "http.GET") == []


def test_multiple_requests_produce_multiple_spans(client_and_exporter):
    client, exp = client_and_exporter
    for _ in range(3):
        client.post("/api/v1/execute", json={})
    spans = _by_name(exp, "http.POST")
    assert len(spans) == 3


def test_404_labels_status_code(client_and_exporter):
    client, exp = client_and_exporter
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    spans = _by_name(exp, "http.GET")
    assert len(spans) == 1
    assert spans[0].attributes["http.status_code"] == 404


def test_request_succeeds_when_tracing_disabled(client_and_exporter):
    from ag import tracing

    client, exp = client_and_exporter
    tracing._ENABLED = False
    tracing._PROVIDER = None
    r = client.post("/api/v1/execute", json={"x": 1})
    assert r.status_code == 200
    assert r.json()["echo"] == {"x": 1}
