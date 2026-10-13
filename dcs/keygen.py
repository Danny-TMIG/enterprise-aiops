"""Generate an Ed25519 signing key for dcs.

Writes dcs/key.hex (private, hex) and dcs/key.pub.hex (public, hex).
Files are gitignored. Run once per machine.
"""

from __future__ import annotations  # pragma: no cover

import sys  # pragma: no cover
from pathlib import Path  # pragma: no cover

from cryptography.hazmat.primitives import serialization  # pragma: no cover
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,  # pragma: no cover
)

ROOT = Path(__file__).resolve().parent


def generate(force: bool = False) -> int:  # pragma: no cover
    priv_path = ROOT / "key.hex"
    pub_path = ROOT / "key.pub.hex"

    if priv_path.exists() and not force:  # pragma: no cover
        print("key already exists at " + str(priv_path) + " (use --force to overwrite)")
        return 0  # pragma: no cover

    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_bytes = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    priv_path.write_text(priv_bytes.hex())
    pub_path.write_text(pub_bytes.hex())
    priv_path.chmod(0o600)

    print("wrote " + str(priv_path))
    print("wrote " + str(pub_path))
    print("add to .gitignore: dcs/key.hex dcs/key.pub.hex")
    return 0  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    force = "--force" in sys.argv
    raise SystemExit(generate(force=force))  # pragma: no cover
