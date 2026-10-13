#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sys
from pathlib import Path

KEY_ENV = "AIOPS_SBOM_KEY"
DEFAULT = "dev-sbom-key-change-me"


def main(argv) -> int:
    if len(argv) != 3:
        print("usage: verify_sbom.py <sbom.json> <sig>", file=sys.stderr)
        return 2
    src, sigf = Path(argv[1]), Path(argv[2])
    if not src.exists():
        print(f"missing: {src}", file=sys.stderr); return 1
    if not sigf.exists():
        print(f"missing: {sigf}", file=sys.stderr); return 1
    key = os.environ.get(KEY_ENV, DEFAULT).encode()
    expected = hmac.new(
        key, hashlib.sha256(src.read_bytes()).digest(), hashlib.sha256
    ).digest()
    got = base64.b64decode(sigf.read_bytes())
    if hmac.compare_digest(expected, got):
        print("  SBOM signature VALID")
        return 0
    print("  SBOM signature INVALID", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
