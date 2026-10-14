"""Tests that ac.app actually instruments requests.

Uses FastAPI's TestClient (backed by httpx) to hit the real ASGI app.
Asserts that after N requests, the Prometheus exposition shows N.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from ac.app import app, metrics


@pytest.fixture
def client(monkeypatch):
    """Fresh Metrics instance per test so counters start at zero.

    Also sets SOVEREIGN_NODE_ID so the /healthz probe reports ok instead of
    down. Any real deployment has this var; a bare pytest process does not.
    """
    from ag.metrics import Metrics
    from ag.settings import reset_settings_cache

    monkeypatch.setenv("SOVEREIGN_NODE_ID", "test-node")
    reset_settings_cache()

    app.state.metrics = Metrics(namespace="sovereign")
    with TestClient(app) as c:
        yield c

    reset_settings_cache()


def _scrape(client: TestClient) -> str:
    return client.get("/metrics").text


def _series(body: str, name: str, **labels: str) -> str | None:
    """Find a line matching `name{...labels...} value` and return its value."""
    # Build a label predicate — order-independent.
    for line in body.splitlines():
        if not line.startswith(name + "{"):
            continue
        head, _, value = line.rpartition(" ")
        if all(f'{k}="{v}"' in head for k, v in labels.items()):
            return value
    return None


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------
def test_counter_increments_across_two_requests(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/healthz").status_code == 200

    body = _scrape(client)
    # /healthz is skipped by the middleware — that's by design. So verify
    # the counter for a *tracked* route.
    r1 = client.post("/api/v1/execute", json={"a": 1})
    r2 = client.post("/api/v1/execute", json={"a": 2})
    assert r1.status_code == 200
    assert r2.status_code == 200

    body = _scrape(client)
    value = _series(
        body,
        "sovereign_requests_total",
        method="POST",
        path="/api/v1/execute",
        status_class="2",
    )
    assert value == "2.0", f"expected 2.0, got {value!r}\n{body}"


def test_healthz_is_not_instrumented(client):
    client.get("/healthz")
    body = _scrape(client)
    assert _series(body, "sovereign_requests_total", path="/healthz") is None


def test_metrics_endpoint_is_not_instrumented(client):
    client.get("/metrics")
    body = _scrape(client)
    assert _series(body, "sovereign_requests_total", path="/metrics") is None


def test_latency_histogram_gets_observations(client):
    client.post("/api/v1/execute", json={})
    body = _scrape(client)
    # Histogram _count should be 1 for the tracked route.
    count_lines = [
        l for l in body.splitlines()
        if l.startswith("sovereign_request_duration_seconds_count")
        and 'path="/api/v1/execute"' in l
    ]
    assert count_lines, body
    assert count_lines[0].rstrip().endswith(" 1.0")


def test_route_template_not_concrete_url(client):
    """Path label must be the route template, not the URL."""
    client.post("/api/v1/execute", json={})
    body = _scrape(client)
    # If we used request.url.path we'd see the same string, but this test
    # pins the contract: it must be the *template* used for routing.
    assert 'path="/api/v1/execute"' in body


def test_unmatched_route_is_labeled_unmatched(client):
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    body = _scrape(client)
    value = _series(
        body,
        "sovereign_requests_total",
        method="GET",
        path="unmatched",
        status_class="4",
    )
    assert value == "1.0", f"expected 1.0, got {value!r}\n{body}"


def test_status_class_reflects_actual_code(client):
    # 404 on a real route prefix
    client.get("/does-not-exist")
    body = _scrape(client)
    # Must be labeled 4, not 2.
    assert 'status_class="4"' in body
    # And no 2-class series for that path.
    assert not re.search(
        r'sovereign_requests_total\{[^}]*path="unmatched"[^}]*status_class="2"',
        body,
    )


# ---------------------------------------------------------------------------
# Failure mode: metrics recorder raises, request still succeeds
# ---------------------------------------------------------------------------
def test_request_succeeds_even_if_metrics_raises(client, monkeypatch):
    class Boom:
        def record(self, **kwargs):
            raise RuntimeError("metrics exploded")

        def record_exception(self, **kwargs):
            raise RuntimeError("metrics exploded")

    monkeypatch.setattr(client.app.state, "metrics", Boom())
    r = client.post("/api/v1/execute", json={"x": 1})
    assert r.status_code == 200
    assert r.json()["echo"] == {"x": 1}


# ---------------------------------------------------------------------------
# Content type of /metrics
# ---------------------------------------------------------------------------
def test_metrics_endpoint_content_type(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")


def test_execute_endpoint_returns_payload(client):
    r = client.post("/api/v1/execute", json={"hello": "world"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "success"
    assert body["echo"] == {"hello": "world"}
