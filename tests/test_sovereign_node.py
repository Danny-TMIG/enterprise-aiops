"""End-to-end test of the sovereign node pipeline (no TestClient)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def isolated_ledger(tmp_path, monkeypatch):
    """Point the node at a fresh ledger for each test."""
    import sovereign.node as node_mod
    from sovereign.ledger import Ledger
    ledger = Ledger(tmp_path / "ledger.jsonl")
    monkeypatch.setattr(node_mod, "LEDGER", ledger)
    return ledger


def _call_chat(content: str):
    """Call the FastAPI handler directly, bypassing HTTP."""
    import sovereign.node as node_mod
    from sovereign.node import ChatRequest, Message
    req = ChatRequest(
        model="tiny-local",
        messages=[Message(role="user", content=content)],
    )
    return node_mod.chat(req)


def test_health():
    import sovereign.node as node_mod
    body = node_mod.health()
    assert body["status"] == "ok"
    assert "node_id" in body


def test_chat_completion_wire_format(isolated_ledger):
    body = _call_chat("hello")
    for key in ("id", "object", "created", "model", "usage", "choices"):
        assert key in body
    assert body["object"] == "chat.completion"
    for key in ("prompt_tokens", "completion_tokens", "total_tokens",
                "completion_tokens_details"):
        assert key in body["usage"]
    assert body["choices"][0]["message"]["role"] == "assistant"
    assert body["choices"][0]["finish_reason"] == "stop"


def test_ledger_records_request(isolated_ledger):
    _call_chat("one")
    _call_chat("two")
    lines = isolated_ledger.path.read_text().strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert second["prev_hash"] == first["row_hash"]


def test_ledger_verifies(isolated_ledger):
    for i in range(3):
        _call_chat(f"msg {i}")
    checked, valid, errors = isolated_ledger.verify()
    assert checked == 3
    assert valid == 3
    assert errors == []


def test_ledger_detects_tamper(isolated_ledger):
    """Tampering with row N invalidates row N and every row after it.

    Row 0 fails because its row_hash no longer matches its contents.
    Row 1 fails because its prev_hash points at the old row 0 hash.
    That is the correct property of a hash-chained ledger.
    """
    _call_chat("a")
    _call_chat("b")
    lines = isolated_ledger.path.read_text().splitlines()
    row = json.loads(lines[0])
    row["completion_tokens"] = 99999
    lines[0] = json.dumps(row)
    isolated_ledger.path.write_text("\n".join(lines) + "\n")
    checked, valid, errors = isolated_ledger.verify()
    assert checked == 2
    assert valid == 0, "no row after a tampered row can verify"
    assert any("row_hash mismatch" in e for e in errors), "row 0 must fail on hash"
    assert any("prev_hash mismatch" in e for e in errors), "row 1 must fail on chain"
