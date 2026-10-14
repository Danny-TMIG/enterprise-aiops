#!/usr/bin/env python3
"""seal_frontend.py — hash dist/ and write deploy/ledgers/ledger_frontend_build.json."""
from __future__ import annotations
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LEDGER = ROOT / "deploy" / "ledgers" / "ledger_frontend_build.json"


def hash_dir(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(path)).encode())
            h.update(b"\x00")
            h.update(p.read_bytes())
            h.update(b"\x00")
    return h.hexdigest()


def main() -> int:
    if not DIST.exists():
        print("seal_frontend: dist/ does not exist — run `npm run build` first", file=sys.stderr)
        return 2
    digest = hash_dir(DIST)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ledger": "frontend_build",
        "sealed_at": time.time(),
        "dist_root": str(DIST.relative_to(ROOT)),
        "sha256": digest,
        "manifest": json.loads((ROOT / "catalog" / "frontend_build_manifest.json").read_text())
    }
    LEDGER.write_text(json.dumps(entry, indent=2) + "\n")
    print(f"sealed frontend build -> {digest[:16]}...")
    print(f"  ledger: {LEDGER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
