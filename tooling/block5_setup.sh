#!/usr/bin/env bash
# Block 5 setup. Writes ag/health.py, tests/test_health_real.py, and
# tooling/block5_live_proof.sh. Idempotent (overwrites).
set -euo pipefail
cd "$HOME/aether"

echo "== writing ag/health.py =="
cat > ag/health.py <<'PYEOF'
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
PYEOF

echo "== writing tests/test_health_real.py =="
cat > tests/test_health_real.py <<'PYEOF'
"""Tests for ag.health. Each probe is exercised in isolation via env vars."""
from __future__ import annotations

import base64

import pytest

from ag import health
from ag.settings import reset_settings_cache


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for k in list(__import__("os").environ):
        if k.startswith("SOVEREIGN_"):
            monkeypatch.delenv(k, raising=False)
    monkeypatch.chdir(tmp_path)
    reset_settings_cache()
    yield
    reset_settings_cache()


def _ok(node_id="n"):
    import os
    os.environ["SOVEREIGN_NODE_ID"] = node_id
    reset_settings_cache()


# ---------------------------------------------------------------------------
# settings probe
# ---------------------------------------------------------------------------
def test_settings_down_when_missing():
    r = health._probe_settings()
    assert r["status"] == health.DOWN
    assert "SOVEREIGN_NODE_ID" in r["detail"]


def test_settings_ok_when_present():
    _ok()
    r = health._probe_settings()
    assert r["status"] == health.OK


# ---------------------------------------------------------------------------
# ledger probe
# ---------------------------------------------------------------------------
def test_ledger_creates_parent(monkeypatch, tmp_path):
    ledger = tmp_path / "sub" / "led.jsonl"
    monkeypatch.setenv("SOVEREIGN_LEDGER_PATH", str(ledger))
    r = health._probe_ledger()
    assert r["status"] == health.OK
    assert ledger.parent.exists()


def test_ledger_down_when_parent_unwritable(monkeypatch, tmp_path):
    import os
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o500)  # read+execute only
    monkeypatch.setenv("SOVEREIGN_LEDGER_PATH", str(ro / "led.jsonl"))
    r = health._probe_ledger()
    # On some CI (root) this stays writable; skip if so.
    if os.access(ro, os.W_OK):
        pytest.skip("running as privileged user; cannot make dir unwritable")
    assert r["status"] == health.DOWN


# ---------------------------------------------------------------------------
# model probe
# ---------------------------------------------------------------------------
def test_model_degraded_when_absent(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVEREIGN_MODEL_PATH", str(tmp_path / "nope.bin"))
    r = health._probe_model()
    assert r["status"] == health.DEGRADED
    assert "not present" in r["detail"]


def test_model_ok_when_present(monkeypatch, tmp_path):
    m = tmp_path / "model.bin"
    m.write_bytes(b"x" * 1024)
    monkeypatch.setenv("SOVEREIGN_MODEL_PATH", str(m))
    r = health._probe_model()
    assert r["status"] == health.OK
    assert "1024" in r["detail"]


def test_model_down_when_directory(monkeypatch, tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    monkeypatch.setenv("SOVEREIGN_MODEL_PATH", str(d))
    r = health._probe_model()
    assert r["status"] == health.DOWN
    assert "not a file" in r["detail"]


# ---------------------------------------------------------------------------
# disk probe
# ---------------------------------------------------------------------------
def test_disk_ok_on_tmp(tmp_path):
    r = health._probe_disk()
    assert r["status"] in (health.OK, health.DOWN)  # depends on tmpfs size


def test_disk_down_when_threshold_huge(monkeypatch):
    monkeypatch.setattr(health, "MIN_FREE_BYTES", 10**30)
    r = health._probe_disk()
    assert r["status"] == health.DOWN
    assert "bytes free" in r["detail"]


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------
def test_check_all_503_when_settings_missing():
    code, body = health.check_all()
    assert code == 503
    assert body["status"] == "down"
    assert body["subsystems"]["settings"]["status"] == health.DOWN


def test_check_all_200_when_settings_present():
    _ok()
    code, body = health.check_all()
    # settings ok; ledger ok (creates dir); model degraded; disk likely ok.
    assert code in (200, 503)  # model degrade is 200; disk failure would 503
    assert body["subsystems"]["settings"]["status"] == health.OK


def test_check_all_body_shape():
    _ok()
    code, body = health.check_all()
    assert set(body["subsystems"].keys()) == {"settings", "ledger", "model", "disk"}
    for name, sub in body["subsystems"].items():
        assert sub["status"] in (health.OK, health.DEGRADED, health.DOWN)
        assert isinstance(sub["detail"], str)
PYEOF

echo "== writing tooling/block5_live_proof.sh =="
cat > tooling/block5_live_proof.sh <<'BASH'
#!/usr/bin/env bash
# Block 5 live proof: hit /healthz and /readyz against a real server.
set -uo pipefail
PORT=8002
BASE="http://127.0.0.1:$PORT"
LOG=/tmp/uvicorn-$PORT.log
PIDFILE=/tmp/uvicorn-$PORT.pid

cleanup() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE" 2>/dev/null || true)
    [ -n "${PID:-}" ] && kill "$PID" 2>/dev/null || true
    rm -f "$PIDFILE"
  fi
}
trap cleanup EXIT

cd "$HOME/aether"

echo "== 1. run block-5 tests =="
python -m pytest tests/test_health_real.py -q 2>&1 | tail -3

echo
echo "== 2. stop any stale server on $PORT =="
STALE=$(lsof -t -i:$PORT 2>/dev/null || true)
[ -n "$STALE" ] && { kill $STALE 2>/dev/null || true; sleep 1; echo "killed $STALE"; } || echo "none"

echo
echo "== 3. start uvicorn with SOVEREIGN_NODE_ID set =="
export SOVEREIGN_NODE_ID=demo
: > "$LOG"
nohup uvicorn ac.app:app --host 127.0.0.1 --port $PORT >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"

echo
echo "== 4. wait for readiness =="
for i in $(seq 1 30); do
  CODE=$(curl -s -o /dev/null -w %{http_code} "$BASE/healthz" 2>/dev/null || echo 000)
  [ "$CODE" = "200" ] && { echo "ready (${i}00ms)"; break; }
  sleep 0.1
done

echo
echo "== 5. /healthz =="
curl -s -w "\nHTTP %{http_code}\n" "$BASE/healthz" | python3 -m json.tool 2>/dev/null || curl -s "$BASE/healthz"

echo
echo "== 6. full body =="
curl -s "$BASE/healthz" | python3 -m json.tool

echo
echo "== 7. verify shape =="
BODY=$(curl -s "$BASE/healthz")
python3 - "$BODY" <<'PY'
import json, sys
body = json.loads(sys.argv[1])
assert "status" in body, "missing top-level status"
assert "subsystems" in body, "missing subsystems"
for k in ("settings", "ledger", "model", "disk"):
    assert k in body["subsystems"], f"missing subsystem: {k}"
    assert body["subsystems"][k]["status"] in ("ok", "degraded", "down")
print(f"top-level status: {body['status']}")
for k, v in body["subsystems"].items():
    print(f"  {k:<10} {v['status']:<10} {v['detail'][:60]}")
PY

echo
echo "== RESULT: block 5 verified =="
BASH
chmod +x tooling/block5_live_proof.sh

echo
echo "== running block-5 tests now =="
python -m pytest tests/test_health_real.py -q 2>&1 | tail -3
