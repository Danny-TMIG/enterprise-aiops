"""DSSE envelope sealing with Ed25519.

Asymmetric signature. The public key is embedded in the envelope
so any holder can verify without a shared secret. Private key is
stored at ~/.mesh-seed/seal_key.pem with 0600 perms, generated on
first use. Rotation moves the old key to <path>.bak.<ts>.

API unchanged from the HMAC version:
    seal(payload, keyid) -> envelope
    verify_seal(envelope, keyid, pubkey=None) -> bool
    unwrap(envelope) -> payload
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any

KEY_DIR = Path.home() / ".mesh-seed"
KEY_PATH = KEY_DIR / "seal_key.pem"
PUB_PATH = KEY_DIR / "seal_pub.pem"


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True,
                      separators=(",", ":"),
                      default=str).encode()


def _load_or_create_key():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )

    if KEY_PATH.exists():
        raw = KEY_PATH.read_bytes()
        key = serialization.load_pem_private_key(raw, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise RuntimeError("key file is not Ed25519")
        return key

    KEY_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(KEY_DIR, 0o700)
    except OSError:
        pass
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    KEY_PATH.write_bytes(pem)
    try:
        os.chmod(KEY_PATH, 0o600)
    except OSError:
        pass
    pub_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PUB_PATH.write_bytes(pub_pem)
    try:
        os.chmod(PUB_PATH, 0o644)
    except OSError:
        pass
    return key


def seal(payload: dict[str, Any],
         keyid: str | None = None) -> dict[str, Any]:
    from cryptography.hazmat.primitives import serialization
    key = _load_or_create_key()
    body = _canonical(payload)
    sig = key.sign(body)
    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return {
        "payloadType": "application/vnd.mesh-seed.proof-object+json",
        "payload": base64.b64encode(body).decode(),
        "signatures": [{
            "keyid": keyid or "default",
            "alg": "Ed25519",
            "sig": base64.b64encode(sig).decode(),
            "pub": base64.b64encode(pub).decode(),
        }],
    }


def verify_seal(envelope: dict[str, Any],
                keyid: str | None = None,
                pubkey: bytes | None = None) -> bool:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PublicKey,
    )
    try:
        body = base64.b64decode(envelope["payload"])
        for s in envelope.get("signatures", []):
            if keyid and s.get("keyid") != keyid:
                continue
            if s.get("alg") != "Ed25519":
                continue
            pub = pubkey or base64.b64decode(s["pub"])
            sig = base64.b64decode(s["sig"])
            try:
                Ed25519PublicKey.from_public_bytes(pub).verify(sig, body)
                return True
            except InvalidSignature:
                continue
        return False
    except Exception:
        return False


def unwrap(envelope: dict[str, Any]) -> dict[str, Any]:
    body = base64.b64decode(envelope["payload"])
    return json.loads(body.decode())


def rotate(keyid: str | None = None) -> str:
    backup: Path | None = None
    if KEY_PATH.exists():
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        backup = KEY_PATH.with_name(f"seal_key.pem.bak.{ts}")
        KEY_PATH.rename(backup)
        if PUB_PATH.exists():
            PUB_PATH.rename(backup.with_name(backup.name.replace(
                "seal_key.pem", "seal_pub.pem")))
    _load_or_create_key()
    return str(backup) if backup else "<no prior key>"


def public_key_pem() -> bytes:
    from cryptography.hazmat.primitives import serialization
    key = _load_or_create_key()
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


DEFAULT_KEY = b'enterprise_aiops_default_key_32bytes_min'
