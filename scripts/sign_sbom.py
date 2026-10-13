#!/usr/bin/env python3
"""Sign SBOM with HMAC-SHA256. Writes the signature file to disk."""
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
        print("usage: sign_sbom.py <sbom.json> <out.sig>", file=sys.stderr)
        return 2
    src, dst = Path(argv[1]), Path(argv[2])
    if not src.exists():
        print(f"missing: {src}", file=sys.stderr)
        return 1
    key = os.environ.get(KEY_ENV, DEFAULT).encode()
    digest = hashlib.sha256(src.read_bytes()).digest()
    sig = hmac.new(key, digest, hashlib.sha256).digest()
    dst.write_bytes(base64.b64encode(sig))
    print(f"  wrote {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
