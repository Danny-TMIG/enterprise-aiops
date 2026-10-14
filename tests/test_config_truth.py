"""Config must match reality at startup."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _config():
    return json.loads((ROOT / "sovereign" / "config.json").read_text())


def test_backend_is_declared():
    cfg = _config()
    assert cfg["backend"] in cfg["backends"], f"backend {cfg['backend']} not in backends"


def test_backend_is_verified():
    cfg = _config()
    assert cfg["backends"][cfg["backend"]]["verified"] is True


def test_no_stale_torch_backend():
    cfg = _config()
    assert "torch-mps" not in cfg["backends"], "stale backend remains"


def test_ledger_rotation_declared():
    cfg = _config()
    assert cfg["ledger_max_bytes"] > 0


def test_max_concurrency_declared():
    cfg = _config()
    assert cfg["max_concurrency"] >= 1
