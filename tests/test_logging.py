"""Tests for ag.logging.

Assertions focus on observable behaviour: what does a record look like on
the wire, and does configuring twice leak handlers?
"""
from __future__ import annotations

import io
import json
import logging as stdlib_logging

import pytest

from ag import logging as ag_logging
from ag.logging import (
    JsonFormatter,
    bind_context,
    clear_context,
    configure_logging,
    get_logger,
)


@pytest.fixture(autouse=True)
def clean_root_and_ctx():
    """Detach all handlers and reset context between tests."""
    root = stdlib_logging.getLogger()
    saved = list(root.handlers)
    root.handlers = []
    clear_context()
    yield
    for h in list(root.handlers):
        root.removeHandler(h)
    root.handlers = saved
    clear_context()
    ag_logging._CONFIGURED = False


def _capture(record: stdlib_logging.LogRecord) -> dict:
    return json.loads(JsonFormatter().format(record))


def _make_record(**extra) -> stdlib_logging.LogRecord:
    r = stdlib_logging.LogRecord(
        name="test",
        level=stdlib_logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    for k, v in extra.items():
        setattr(r, k, v)
    return r


def test_json_formatter_basic_fields():
    out = _capture(_make_record())
    assert out["level"] == "INFO"
    assert out["logger"] == "test"
    assert out["msg"] == "hello world"
    assert "ts" in out
    assert out["ts"].endswith("Z")


def test_json_formatter_picks_up_extras():
    r = _make_record()
    r.request_id = "abc-123"  # type: ignore[attr-defined]
    out = _capture(r)
    assert out["request_id"] == "abc-123"


def test_json_formatter_serializes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        r = stdlib_logging.LogRecord(
            "test", stdlib_logging.ERROR, __file__, 1, "failed", None, sys.exc_info()
        )
    out = _capture(r)
    assert "ValueError: boom" in out["exc_info"]
    assert "\n" in out["exc_info"]  # traceback survives as one JSON string


def test_json_formatter_default_str_for_unknown_types():
    from pathlib import Path

    r = _make_record()
    r.path = Path("/tmp/x")  # type: ignore[attr-defined]
    out = _capture(r)
    assert out["path"] == "/tmp/x"


def test_context_is_attached_to_record():
    bind_context(request_id="r-1", trace_id="t-1")
    out = _capture(_make_record())
    assert out["request_id"] == "r-1"
    assert out["trace_id"] == "t-1"


def test_extra_overrides_context():
    bind_context(request_id="ctx-value")
    r = _make_record()
    r.request_id = "extra-value"  # type: ignore[attr-defined]
    out = _capture(r)
    # Explicit record fields are applied after context, so they win.
    assert out["request_id"] == "extra-value"


def test_clear_context():
    bind_context(request_id="r-1")
    clear_context()
    out = _capture(_make_record())
    assert "request_id" not in out


def test_configure_logging_is_idempotent():
    configure_logging(level="WARNING")
    first = [h for h in stdlib_logging.getLogger().handlers if getattr(h, "_ag_json_handler", False)]
    configure_logging(level="WARNING")
    second = [h for h in stdlib_logging.getLogger().handlers if getattr(h, "_ag_json_handler", False)]
    assert len(first) == 1
    assert len(second) == 1  # not stacked


def test_configure_logging_with_file(tmp_path):
    log_file = tmp_path / "app.jsonl"
    configure_logging(level="INFO", file=log_file)
    get_logger("t").info("hello", extra={"k": "v"})
    for h in stdlib_logging.getLogger().handlers:
        h.flush()
    lines = [l for l in log_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["msg"] == "hello"
    assert rec["k"] == "v"


def test_configure_logging_emits_to_stderr(capsys):
    configure_logging(level="INFO")
    get_logger("t").info("hi", extra={"n": 1})
    captured = capsys.readouterr()
    rec = json.loads(captured.err.strip().splitlines()[-1])
    assert rec["msg"] == "hi"
    assert rec["n"] == 1


def test_configure_logging_respects_level(capsys):
    configure_logging(level="WARNING")
    log = get_logger("t")
    log.info("silent")
    log.warning("loud")
    captured = capsys.readouterr()
    lines = [l for l in captured.err.splitlines() if l.strip()]
    assert all(json.loads(l)["msg"] == "loud" for l in lines)


def test_ag_logging_does_not_shadow_stdlib():
    import logging
    assert logging is stdlib_logging
    assert logging.getLogger is stdlib_logging.getLogger
