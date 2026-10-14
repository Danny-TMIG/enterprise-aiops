"""Subsystem health probes.

Each probe returns a dict: {"status": "ok"|"degraded"|"down", "detail": str}.
A probe never raises; a failing check is reported as "down" with a message.

The top-level `check_all()` collapses the per-subsystem results into a
single status and an aggregate code: 200 if all ok, 503 if any down.
"""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any

log = logging.getLogger("ag.health")

OK = "ok"
DEGRADED = "degraded"
DOWN = "down"

# How much free space (bytes) we require on the ledger's filesystem.
MIN_FREE_BYTES = 100 * 1024 * 1024  # 100 MiB


def _probe_settings() -> dict[str, Any]:
    try:
        from ag.settings import SettingsError, get_settings

        s = get_settings()
        return {"status": OK, "detail": f"node_id={s.node_id}"}
    except SettingsError as e:
        return {"status": DOWN, "detail": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"status": DOWN, "detail": f"unexpected: {e}"}


def _probe_ledger() -> dict[str, Any]:
    """Ledger is healthy if its parent dir exists and is writable."""
    ledger_path = Path(os.environ.get("SOVEREIGN_LEDGER_PATH", "sovereign/ledger.jsonl"))
    parent = ledger_path.parent
    try:
        if not parent.exists():
            # Try to create it — a cold start should be able to.
            parent.mkdir(parents=True, exist_ok=True)
        if not os.access(parent, os.W_OK):
            return {"status": DOWN, "detail": f"not writable: {parent}"}
        if ledger_path.exists() and not os.access(ledger_path, os.W_OK):
            return {"status": DOWN, "detail": f"ledger exists but not writable: {ledger_path}"}
        return {"status": OK, "detail": str(ledger_path)}
    except Exception as e:  # noqa: BLE001
        return {"status": DOWN, "detail": f"{type(e).__name__}: {e}"}


def _probe_model() -> dict[str, Any]:
    """Model path is healthy if it exists and is readable. Absent = degraded."""
    raw = os.environ.get("SOVEREIGN_MODEL_PATH", "models/tiny/model.safetensors")
    path = Path(raw)
    try:
        if not path.exists():
            return {"status": DEGRADED, "detail": f"not present: {path}"}
        if not path.is_file():
            return {"status": DOWN, "detail": f"not a file: {path}"}
        if not os.access(path, os.R_OK):
            return {"status": DOWN, "detail": f"not readable: {path}"}
        size = path.stat().st_size
        return {"status": OK, "detail": f"{path} ({size} bytes)"}
    except Exception as e:  # noqa: BLE001
        return {"status": DOWN, "detail": f"{type(e).__name__}: {e}"}


def _probe_disk() -> dict[str, Any]:
    """Disk is healthy if the ledger's filesystem has >= MIN_FREE_BYTES free."""
    ledger_path = Path(os.environ.get("SOVEREIGN_LEDGER_PATH", "sovereign/ledger.jsonl"))
    anchor = ledger_path.parent if ledger_path.parent.exists() else Path.cwd()
    try:
        usage = shutil.disk_usage(anchor)
        free = usage.free
        if free < MIN_FREE_BYTES:
            return {
                "status": DOWN,
                "detail": f"{free} bytes free on {anchor} (< {MIN_FREE_BYTES})",
            }
        return {"status": OK, "detail": f"{free} bytes free on {anchor}"}
    except Exception as e:  # noqa: BLE001
        return {"status": DOWN, "detail": f"{type(e).__name__}: {e}"}


_PROBES = {
    "settings": _probe_settings,
    "ledger": _probe_ledger,
    "model": _probe_model,
    "disk": _probe_disk,
}


def check_all() -> tuple[int, dict[str, Any]]:
    """Return (http_status, body). 200 if all ok, 503 if any down."""
    subsystems: dict[str, Any] = {}
    any_down = False
    any_degraded = False
    for name, fn in _PROBES.items():
        try:
            result = fn()
        except Exception as e:  # noqa: BLE001 - belt-and-suspenders
            result = {"status": DOWN, "detail": f"probe crashed: {e}"}
        subsystems[name] = result
        if result["status"] == DOWN:
            any_down = True
        elif result["status"] == DEGRADED:
            any_degraded = True

    if any_down:
        overall = "down"
        code = 503
    elif any_degraded:
        overall = "degraded"
        code = 200
    else:
        overall = "ok"
        code = 200

    return code, {"status": overall, "subsystems": subsystems}
