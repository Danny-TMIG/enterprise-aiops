"""Structured JSON logging for the Aether stack.

Design constraints, in order of priority:

1. Do not shadow the stdlib ``logging`` module. This file lives at
   ``ag/logging.py``; every internal use imports the stdlib as ``_log``.
2. Importing this module has no side effects. Callers opt in via
   ``configure_logging()``.
3. Output is one JSON object per line on stderr (stdlib default) or a
   configured file. No multi-line tracebacks unless ``exc_info`` is set,
   in which case they are a single JSON field with embedded newlines.
4. Log level is read from ``ag.settings.get_settings()`` at configure time.
   Passing ``level=...`` overrides.
5. Request/trace IDs propagate via contextvars; async tasks see their own.
"""
from __future__ import annotations

import json
import logging as _log
import logging.handlers as _handlers
import sys
import time
from contextvars import ContextVar
from pathlib import Path
from typing import Any

# Re-export so callers can `from ag.logging import Logger` if they want a type
Logger = _log.Logger
LogRecord = _log.LogRecord

# ---------------------------------------------------------------------------
# Context: request_id, trace_id, etc. propagate through async tasks.
# ---------------------------------------------------------------------------
_ctx: ContextVar[dict[str, Any]] = ContextVar("ag_logging_ctx", default={})


def bind_context(**fields: Any) -> None:
    """Attach fields to the current async context. Merges with existing."""
    current = dict(_ctx.get())
    current.update(fields)
    _ctx.set(current)


def clear_context() -> None:
    """Drop all context fields. Call at request boundaries if not using a middleware."""
    _ctx.set({})


def _current_context() -> dict[str, Any]:
    return _ctx.get()


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------
_LEVEL_NAMES = {
    _log.DEBUG: "DEBUG",
    _log.INFO: "INFO",
    _log.WARNING: "WARNING",
    _log.ERROR: "ERROR",
    _log.CRITICAL: "CRITICAL",
}


class JsonFormatter(_log.Formatter):
    """Emit one JSON object per record. Stable field names."""

    # Standard record attributes we never copy into `extra`.
    _RESERVED = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "taskName",
    }

    def __init__(self, *, fmt_ts: bool = True) -> None:
        super().__init__()
        self._fmt_ts = fmt_ts

    def format(self, record: _log.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": (
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
                + f".{int(record.msecs):03d}Z"
                if self._fmt_ts
                else record.created
            ),
            "level": _LEVEL_NAMES.get(record.levelno, record.levelname),
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Context fields first so explicit extras can override.
        for k, v in _current_context().items():
            payload[k] = v

        # `extra={...}` passed by the caller.
        for k, v in record.__dict__.items():
            if k in self._RESERVED or k.startswith("_"):
                continue
            payload[k] = v

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        # `default=str` so Path, Decimal, etc. don't crash the handler.
        return json.dumps(payload, separators=(",", ":"), default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_CONFIGURED = False


def _resolve_level(level: str | int | None) -> int:
    if level is None:
        # Import here so ag.logging has no import-time dependency on settings.
        try:
            from ag.settings import get_settings

            level = get_settings().log_level
        except Exception:  # noqa: BLE001 - settings not available; default safely
            level = "INFO"
    if isinstance(level, int):
        return level
    return _log.getLevelName(level.upper())  # type: ignore[return-value]


def configure_logging(
    *,
    level: str | int | None = None,
    file: Path | str | None = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """Configure the root logger for JSON output.

    Idempotent: calling twice replaces the handlers we installed rather
    than stacking them. Handlers installed by other libraries are left alone.
    """
    global _CONFIGURED

    root = _log.getLogger()
    root.setLevel(_resolve_level(level))

    # Remove only our own handlers, and only if we've configured before.
    if _CONFIGURED:
        for h in list(root.handlers):
            if getattr(h, "_ag_json_handler", False):
                root.removeHandler(h)

    formatter = JsonFormatter()

    stream = _log.StreamHandler(stream=sys.stderr)
    stream.setFormatter(formatter)
    stream._ag_json_handler = True  # type: ignore[attr-defined]
    root.addHandler(stream)

    if file is not None:
        fh = _handlers.RotatingFileHandler(
            filename=str(file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        fh.setFormatter(formatter)
        fh._ag_json_handler = True  # type: ignore[attr-defined]
        root.addHandler(fh)

    _CONFIGURED = True


def get_logger(name: str) -> Logger:
    """Return a logger. Assumes ``configure_logging()`` has been called."""
    return _log.getLogger(name)
