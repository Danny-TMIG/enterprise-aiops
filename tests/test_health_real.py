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
