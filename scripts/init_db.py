#!/usr/bin/env python3
"""Initialise every database layer. Idempotent."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from app.db.migrations import run_migrations
    HAS_DB = True
except Exception:
    HAS_DB = False


def main() -> int:
    if not HAS_DB:
        print("  app.db not installed; nothing to do")
        return 0
    print("  running migrations")
    report = run_migrations()
    for k, v in report.items():
        print(f"    {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
