"""Health endpoint reports per-subsystem status."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_health_has_subsystems():
    import sovereign.node as node_mod
    body = node_mod.health()
    assert "subsystems" in body
    for k in ("config", "model", "ledger"):
        assert k in body["subsystems"]
        assert body["subsystems"][k] in ("ok", "degraded", "down")


def test_health_top_level_status():
    import sovereign.node as node_mod
    body = node_mod.health()
    assert body["status"] in ("ok", "degraded", "down")


def test_health_config_is_ok():
    import sovereign.node as node_mod
    body = node_mod.health()
    assert body["subsystems"]["config"] == "ok"
