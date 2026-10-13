"""Signature verification. HMAC-SHA256 reference implementation."""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Protocol


def digest_of(payload: bytes | str) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    reason: str = ""


class Verifier(Protocol):
    def sign(self, payload: bytes) -> bytes: ...
    def verify(self, payload: bytes, signature: bytes) -> bool: ...


class HMACVerifier:
    def __init__(self, key: bytes) -> None:
        if not key:
            raise ValueError("key must be non-empty")
        self._key = key

    def sign(self, payload: bytes) -> bytes:
        return hmac.new(self._key, payload, hashlib.sha256).digest()

    def verify(self, payload: bytes, signature: bytes) -> bool:
        return hmac.compare_digest(self.sign(payload), signature)


def verify(payload, signature, verifier: Verifier) -> VerificationResult:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    if isinstance(signature, str):
        try:
            signature = bytes.fromhex(signature)
        except ValueError:
            return VerificationResult(False, "signature is not hex")
    try:
        ok = verifier.verify(payload, signature)
    except Exception as e:
        return VerificationResult(False, type(e).__name__ + ": " + str(e))
    return VerificationResult(True, "") if ok else VerificationResult(False, "signature mismatch")
