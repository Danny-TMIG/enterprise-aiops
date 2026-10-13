"""HMAC-SHA256 signing. Real key, real verify."""
from __future__ import annotations

import hashlib
import hmac
import secrets


def generate_key() -> bytes: return secrets.token_bytes(32)

def key_id(key: bytes) -> str: return hashlib.sha256(key).hexdigest()[:16]

def sign(payload: bytes, key: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()

def verify(payload: bytes, sig: str, key: bytes) -> bool:
    return hmac.compare_digest(sign(payload, key), sig)
