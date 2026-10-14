"""Malformed requests fail with 400, not 500."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _validate(content, role="user", max_tokens=128, temperature=0.0):
    from sovereign.node import ChatRequest, Message, _validate as v
    req = ChatRequest(
        model="tiny-local",
        messages=[Message(role=role, content=content)],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return v(req)


def test_empty_content_rejected():
    assert _validate("") is not None


def test_whitespace_only_content_rejected():
    assert _validate("   ") is not None


def test_bad_role_rejected():
    assert _validate("hello", role="tool") is not None


def test_bad_max_tokens_rejected():
    assert _validate("hello", max_tokens=0) is not None
    assert _validate("hello", max_tokens=99999) is not None


def test_bad_temperature_rejected():
    assert _validate("hello", temperature=-0.5) is not None
    assert _validate("hello", temperature=3.0) is not None


def test_valid_request_passes():
    assert _validate("hello") is None
