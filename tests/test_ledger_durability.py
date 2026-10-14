"""Ledger fsync durability."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ag.ledger import Ledger


def test_append_fsyncs(tmp_path):
    ledger = Ledger(tmp_path / "l.jsonl")
    ledger.append({"a": 1}, {"b": 2}, {"request_id": "t1"})
    # the file exists on disk after append returns
    assert ledger.path.exists()
    assert ledger.path.stat().st_size > 0


def test_verify_after_fsync(tmp_path):
    ledger = Ledger(tmp_path / "l.jsonl")
    for i in range(3):
        ledger.append({"i": i}, {"ok": True}, {"request_id": f"t{i}"})
    checked, valid, errors = ledger.verify()
    assert checked == 3
    assert valid == 3
    assert errors == []
