#!/usr/bin/env python3
"""Deterministic SBOM: sha256 of every source file under app/ and scripts/."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache", ".venv",
             "venv", "node_modules", "build", "dist",
             ".codeql-db", ".codeql-results", ".mypy_cache",
             ".ruff_cache", "*.egg-info"}
SKIP_EXT = {".pyc", ".pyo", ".so", ".dylib", ".dll"}


def iter_files():
    for base in ("app", "scripts"):
        b = ROOT / base
        if not b.exists():
            continue
        for p in sorted(b.rglob("*")):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix in SKIP_EXT:
                continue
            yield p


def main() -> int:
    entries = []
    for p in iter_files():
        rel = str(p.relative_to(ROOT))
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append({"path": rel, "size": p.stat().st_size, "sha256": h})
    root = hashlib.sha256(
        "".join(e["sha256"] for e in entries).encode()
    ).hexdigest()
    print(json.dumps({
        "format": "enterprise-aiops-sbom-v1",
        "entries": entries,
        "count": len(entries),
        "root": root,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
