"""Concurrent requests do not corrupt the ledger."""
from __future__ import annotations
import sys
import threading
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovereign.ledger import Ledger


def test_concurrent_appends_are_serialized(tmp_path):
    ledger = Ledger(tmp_path / "l.jsonl")
    N = 20

    def worker(i):
        ledger.append({"i": i}, {"ok": True}, {"request_id": f"w{i}"})

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    checked, valid, errors = ledger.verify()
    assert checked == N
    assert valid == N
    assert errors == []
