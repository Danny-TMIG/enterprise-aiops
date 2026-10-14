"""Ten capabilities, ten templates, one node."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CAPABILITIES = [
    "translate", "summarize", "answer", "write", "code",
    "factcheck", "creative", "research", "email", "chat",
]


def test_manifest_exists():
    assert (ROOT / "sovereign" / "capabilities.json").is_file()


def test_manifest_declares_ten():
    m = json.loads((ROOT / "sovereign" / "capabilities.json").read_text())
    assert len(m["capabilities"]) == 10
    assert set(m["capabilities"].keys()) == set(CAPABILITIES)


@pytest.mark.parametrize("name", CAPABILITIES)
def test_template_exists(name):
    p = ROOT / "sovereign" / "templates" / f"{name}.txt"
    assert p.is_file(), f"missing template for {name}"
    assert len(p.read_text().strip()) >= 20


@pytest.mark.parametrize("name", CAPABILITIES)
def test_capability_injects_system_message(name):
    import sovereign.node as node_mod
    from sovereign.node import ChatRequest, Message

    req = ChatRequest(
        model="tiny-local",
        capability=name,
        messages=[Message(role="user", content="hello")],
    )
    result = node_mod._apply_capability(req)
    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert result[1]["role"] == "user"
    assert "hello" in result[1]["content"]


def test_no_capability_returns_messages_unchanged():
    import sovereign.node as node_mod
    from sovereign.node import ChatRequest, Message

    req = ChatRequest(
        model="tiny-local",
        capability=None,
        messages=[Message(role="user", content="hello")],
    )
    result = node_mod._apply_capability(req)
    assert len(result) == 1
    assert result[0]["role"] == "user"


def test_unknown_capability_raises():
    import sovereign.node as node_mod
    from sovereign.node import ChatRequest, Message

    req = ChatRequest(
        model="tiny-local",
        capability="not_a_capability",
        messages=[Message(role="user", content="hello")],
    )
    with pytest.raises(ValueError):
        node_mod._apply_capability(req)
