"""Tests for ag.metrics.

Focus: label correctness, boundary cases (500, 404, exception), async
support, and that a broken registry doesn't break the caller.
"""
from __future__ import annotations

import asyncio

import pytest

from ag.metrics import Metrics


def _scrape(m: Metrics) -> str:
    return m.render().decode("utf-8")


def test_counter_increments_on_record():
    m = Metrics()
    m.record(method="GET", path="/items", status_code=200, duration_seconds=0.05)
    body = _scrape(m)
    assert 'sovereign_requests_total{method="GET",path="/items",status_class="2"} 1.0' in body


def test_status_class_buckets_correctly():
    m = Metrics()
    for code in (200, 201, 204):
        m.record(method="POST", path="/x", status_code=code, duration_seconds=0.01)
    for code in (400, 401, 404):
        m.record(method="POST", path="/x", status_code=code, duration_seconds=0.01)
    for code in (500, 503):
        m.record(method="POST", path="/x", status_code=code, duration_seconds=0.01)
    body = _scrape(m)
    assert 'status_class="2"} 3.0' in body
    assert 'status_class="4"} 3.0' in body
    assert 'status_class="5"} 2.0' in body


def test_histogram_observes_duration():
    m = Metrics()
    m.record(method="GET", path="/y", status_code=200, duration_seconds=0.075)
    body = _scrape(m)
    assert "sovereign_request_duration_seconds_count" in body
    assert 'method="GET",path="/y"' in body
    assert "_sum" in body


def test_5xx_also_increments_errors():
    m = Metrics()
    m.record(method="GET", path="/z", status_code=503, duration_seconds=0.1)
    body = _scrape(m)
    assert 'sovereign_request_errors_total{kind="5xx",method="GET",path="/z"} 1.0' in body


def test_4xx_does_not_increment_errors():
    m = Metrics()
    m.record(method="GET", path="/z", status_code=404, duration_seconds=0.01)
    body = _scrape(m)
    assert "sovereign_request_errors_total" not in body or \
           'kind="5xx"' not in body


def test_record_exception_uses_status_class_zero():
    m = Metrics()
    m.record_exception(method="POST", path="/boom", duration_seconds=0.2)
    body = _scrape(m)
    assert 'status_class="0"} 1.0' in body
    assert 'kind="exception"' in body


def test_sync_decorator_records_success():
    m = Metrics()

    @m.track("GET", "/sync")
    def handler(*, state):
        state["status"] = 200
        return "ok"

    assert handler() == "ok"
    body = _scrape(m)
    assert 'status_class="2"} 1.0' in body


def test_sync_decorator_records_exception():
    m = Metrics()

    @m.track("GET", "/explode")
    def handler(*, state):
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError):
        handler()
    body = _scrape(m)
    assert 'status_class="0"} 1.0' in body
    assert 'kind="exception"' in body


def test_async_decorator_awaits_and_records():
    m = Metrics()

    @m.track_async("POST", "/async")
    async def handler(*, state):
        await asyncio.sleep(0)
        state["status"] = 201
        return "made"

    result = asyncio.run(handler())
    assert result == "made"
    body = _scrape(m)
    assert 'status_class="2"} 1.0' in body


def test_async_decorator_records_exception():
    m = Metrics()

    @m.track_async("POST", "/async-boom")
    async def handler(*, state):
        await asyncio.sleep(0)
        raise ValueError("async fail")

    with pytest.raises(ValueError):
        asyncio.run(handler())
    body = _scrape(m)
    assert 'status_class="0"} 1.0' in body
    assert 'kind="exception"' in body


def test_in_flight_is_zero_after_tracked_call():
    m = Metrics()

    @m.track("GET", "/p")
    def handler(*, state):
        state["status"] = 200
        return None

    handler()
    body = _scrape(m)
    assert 'sovereign_requests_in_flight{method="GET",path="/p"} 0.0' in body


def test_in_flight_is_one_during_call():
    m = Metrics()
    seen = {}

    @m.track("GET", "/live")
    def handler(*, state):
        # Inside the call, the gauge should read 1.
        body = _scrape(m)
        seen["during"] = 'sovereign_requests_in_flight{method="GET",path="/live"} 1.0' in body
        state["status"] = 200

    handler()
    assert seen["during"], "in_flight should be 1 while the handler is running"
    after = _scrape(m)
    assert 'sovereign_requests_in_flight{method="GET",path="/live"} 0.0' in after


def test_two_instances_do_not_collide():
    m1 = Metrics(namespace="a")
    m2 = Metrics(namespace="b")
    m1.record(method="GET", path="/x", status_code=200, duration_seconds=0.01)
    m2.record(method="GET", path="/x", status_code=200, duration_seconds=0.01)
    assert "a_requests_total" in _scrape(m1)
    assert "b_requests_total" in _scrape(m2)
    assert "b_requests_total" not in _scrape(m1)


def test_record_swallows_bad_labels(monkeypatch):
    """A broken registry must not raise into the request path."""
    m = Metrics()
    # Force the underlying counter to raise.
    class Boom:
        def labels(self, **kwargs):
            raise RuntimeError("registry exploded")
    monkeypatch.setattr(m, "requests", Boom())
    # Should not raise.
    m.record(method="GET", path="/safe", status_code=200, duration_seconds=0.01)


def test_content_type_is_prometheus_text():
    """The client library chooses the exposition version; we just pass it through."""
    m = Metrics()
    assert m.content_type.startswith("text/plain")
    # Both 0.0.4 (legacy) and 1.0.0 (OpenMetrics-compatible) are valid.
    assert "version=" in m.content_type
    import re
    assert re.search(r"version=\d+\.\d+\.\d+", m.content_type)


def test_help_and_type_lines_present():
    m = Metrics()
    m.record(method="GET", path="/h", status_code=200, duration_seconds=0.01)
    body = _scrape(m)
    assert "# HELP sovereign_requests_total" in body
    assert "# TYPE sovereign_requests_total counter" in body
    assert "# TYPE sovereign_request_duration_seconds histogram" in body


def test_render_is_valid_prometheus_text():
    """Every non-comment line parses as `name{labels} value`."""
    m = Metrics()
    m.record(method="GET", path="/v", status_code=200, duration_seconds=0.01)
    for line in _scrape(m).splitlines():
        if not line or line.startswith("#"):
            continue
        # Split on the last space: everything before is name+labels, after is value.
        head, _, value = line.rpartition(" ")
        assert head, f"malformed line: {line!r}"
        assert value.replace(".", "", 1).replace("+", "", 1).replace("e", "", 1).isdigit() or value in ("+Inf", "-Inf", "NaN"), \
            f"non-numeric value in: {line!r}"
