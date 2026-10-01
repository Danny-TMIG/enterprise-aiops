"""in-toto Statement + DSSE envelope wrapper.

Emits an in-toto v1 Statement whose predicate is the full dcs.self
payload, wrapped in a DSSE envelope. Sigstore-aware consumers
(cosign, rekor, policy-controller) can verify without dcs-specific
tooling.

Signing key resolution order:
  1. DCS_SIGNING_KEY environment variable (path to a hex Ed25519 key)
  2. dcs/key.hex next to this module (produced by `python -m dcs.keygen`)

If neither exists, the envelope is emitted with signatures=[] and
is still a valid DSSE envelope.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE = "https://dcs.dannylabs.example/attestation/v1"


def _digest(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def to_statement(payload: dict, subject_name: str = "dcs-self") -> dict:
    return {
        "_type": STATEMENT_TYPE,
        "subject": [
            {
                "name": subject_name,
                "digest": {"sha256": _digest(payload)},
            }
        ],
        "predicateType": PREDICATE_TYPE,
        "predicate": payload,
    }


def _resolve_key_path() -> str | None:
    env = os.environ.get("DCS_SIGNING_KEY")
    if env:
        return env
    default = Path(__file__).resolve().parent / "key.hex"
    if default.exists():
        return str(default)
    return None


def to_dsse(statement: dict) -> dict:
    payload_bytes = json.dumps(statement, sort_keys=True).encode()
    envelope: dict = {
        "payloadType": "application/vnd.in-toto+json",
        "payload": base64.b64encode(payload_bytes).decode(),
        "signatures": [],
    }

    key_path = _resolve_key_path()
    if not key_path or not Path(key_path).exists():
        return envelope

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        key_hex = Path(key_path).read_text().strip()
        priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex))
        pub_raw = priv.public_key().public_bytes_raw()
        sig = priv.sign(payload_bytes)
        envelope["signatures"].append(
            {
                "keyid": hashlib.sha256(pub_raw).hexdigest()[:16],
                "sig": base64.b64encode(sig).decode(),
                "public": pub_raw.hex(),
                "alg": "ed25519",
            }
        )
    except Exception:
        pass

    return envelope
