"""Tests for ag.settings. No real .env is read."""
from __future__ import annotations

import base64
import os
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from ag.settings import SettingsError, get_settings, reset_settings_cache


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for k in list(os.environ):
        if k.startswith("SOVEREIGN_"):
            monkeypatch.delenv(k, raising=False)
    monkeypatch.chdir(tmp_path)
    reset_settings_cache()
    yield
    reset_settings_cache()


def _write_key(tmp_path: Path, mode: int) -> Path:
    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    p = tmp_path / "k.pem"
    p.write_bytes(pem)
    p.chmod(mode)
    return p


def test_missing_required_raises_with_names():
    with pytest.raises(SettingsError) as ei:
        get_settings()
    assert "SOVEREIGN_NODE_ID" in str(ei.value)


def test_minimal_ok(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "node-01")
    s = get_settings()
    assert s.node_id == "node-01"
    assert s.tensor_swarm_port == 9001


def test_node_id_rejects_whitespace(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "has space")
    with pytest.raises(SettingsError):
        get_settings()


def test_port_range(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_TENSOR_SWARM_PORT", "70000")
    with pytest.raises(SettingsError):
        get_settings()


def test_key_file_must_exist(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ED25519_PRIVATE_KEY_PATH", str(tmp_path / "nope.pem"))
    with pytest.raises(SettingsError):
        get_settings()


def test_key_file_world_readable_rejected(monkeypatch, tmp_path):
    p = _write_key(tmp_path, 0o644)
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ED25519_PRIVATE_KEY_PATH", str(p))
    with pytest.raises(SettingsError):
        get_settings()


def test_key_file_0600_accepted(monkeypatch, tmp_path):
    p = _write_key(tmp_path, 0o600)
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ED25519_PRIVATE_KEY_PATH", str(p))
    s = get_settings()
    assert s.ed25519_private_key_path == p


def test_key_file_group_readable_rejected(monkeypatch, tmp_path):
    p = _write_key(tmp_path, 0o640)
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ED25519_PRIVATE_KEY_PATH", str(p))
    with pytest.raises(SettingsError):
        get_settings()


def test_key_file_0400_accepted(monkeypatch, tmp_path):
    p = _write_key(tmp_path, 0o400)  # owner read-only, no write, no group, no world
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ED25519_PRIVATE_KEY_PATH", str(p))
    s = get_settings()
    assert s.ed25519_private_key_path == p


def test_key_file_0440_rejected(monkeypatch, tmp_path):
    p = _write_key(tmp_path, 0o440)  # group-readable: rejected by design
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ED25519_PRIVATE_KEY_PATH", str(p))
    with pytest.raises(SettingsError):
        get_settings()


def test_salt_must_be_base64(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ENCRYPTION_SALT", "not-base64")
    with pytest.raises(SettingsError):
        get_settings()


def test_salt_too_short_rejected(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ENCRYPTION_SALT", base64.b64encode(b"short").decode())
    with pytest.raises(SettingsError):
        get_settings()


def test_salt_ok(monkeypatch):
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ENCRYPTION_SALT", base64.b64encode(b"x" * 32).decode())
    s = get_settings()
    assert s.encryption_salt is not None


def test_secret_not_leaked_in_repr(monkeypatch):
    plain = base64.b64encode(b"x" * 32).decode()
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "n")
    monkeypatch.setenv("SOVEREIGN_ENCRYPTION_SALT", plain)
    s = get_settings()
    assert plain not in repr(s)


def test_env_overrides_dotenv(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text("SOVEREIGN_NODE_ID=from-dotenv\n")
    monkeypatch.setenv("SOVEREIGN_NODE_ID", "from-env")
    reset_settings_cache()
    assert get_settings().node_id == "from-env"
