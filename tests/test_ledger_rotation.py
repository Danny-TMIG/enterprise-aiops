"""Ledger rotates when it exceeds its max size."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ag.ledger import Ledger


def test_rotation_creates_new_file(tmp_path, monkeypatch):
    # set max_bytes small so rotation triggers fast
    cfg = ROOT / "sovereign" / "config.json"
    data = json.loads(cfg.read_text())
    original = data.get("ledger_max_bytes")
    data["ledger_max_bytes"] = 500
    cfg.write_text(json.dumps(data, indent=2))
    try:
        ledger = Ledger(tmp_path / "l.jsonl")
        for i in range(10):
            ledger.append({"i": i}, {"ok": True}, {"request_id": f"r{i}"})
        # at least one rotation should have happened
        siblings = list(tmp_path.glob("l-*.jsonl"))
        assert siblings, "no rotated files present"
    finally:
        data["ledger_max_bytes"] = original
        cfg.write_text(json.dumps(data, indent=2))
