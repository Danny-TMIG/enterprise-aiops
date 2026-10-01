"""Verify a dcs in-toto DSSE envelope.

Usage:
    python -m dcs.verify_intoto <envelope.json> [--pubkey <hex>]

Exit 0 on success (signed and valid, or unsigned and shaped correctly),
1 on any verification failure.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


def verify(path: Path, external_pubkey: str | None = None) -> int:
    env = json.loads(path.read_text())

    if env.get("payloadType") != "application/vnd.in-toto+json":
        print("FAIL: payloadType is not application/vnd.in-toto+json")
        return 1

    try:
        payload = base64.b64decode(env["payload"])
    except Exception as e:
        print("FAIL: payload not valid base64: " + str(e))
        return 1

    try:
        stmt = json.loads(payload)
    except Exception as e:
        print("FAIL: payload not valid JSON: " + str(e))
        return 1

    if stmt.get("_type") != "https://in-toto.io/Statement/v1":
        print("FAIL: _type is not in-toto v1")
        return 1

    sigs = env.get("signatures", [])
    if not sigs:
        print("UNSIGNED: envelope has 0 signatures (valid but unverified)")
        print("  subject: " + stmt["subject"][0]["name"])
        print("  digest:  sha256:" + stmt["subject"][0]["digest"]["sha256"][:16] + "...")
        return 0

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
    except ImportError:
        print("FAIL: cryptography not installed; cannot verify")
        return 1

    for i, sig in enumerate(sigs):
        pub_hex = sig.get("public") or external_pubkey
        if not pub_hex:
            print("FAIL: signature " + str(i) + " has no public key and no --pubkey given")
            return 1
        try:
            pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
            pub.verify(base64.b64decode(sig["sig"]), payload)
        except InvalidSignature:
            print("FAIL: signature " + str(i) + " INVALID")
            return 1
        except Exception as e:
            print("FAIL: signature " + str(i) + " errored: " + str(e))
            return 1

        if external_pubkey and pub_hex != external_pubkey:
            print("FAIL: signature " + str(i) + " public key does not match --pubkey")
            return 1

    print("OK: " + str(len(sigs)) + " valid signature(s)")
    print("  keyid:   " + sigs[0]["keyid"])
    print("  subject: " + stmt["subject"][0]["name"])
    print("  digest:  sha256:" + stmt["subject"][0]["digest"]["sha256"][:16] + "...")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="in-toto envelope JSON")
    ap.add_argument("--pubkey", default=None, help="optional hex Ed25519 pubkey")
    args = ap.parse_args()
    return verify(Path(args.path), args.pubkey)


if __name__ == "__main__":
    raise SystemExit(main())
