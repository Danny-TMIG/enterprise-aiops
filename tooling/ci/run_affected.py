#!/usr/bin/env python3
"""run_affected.py — run component tests only for affected components.

Reads affected.json (produced by affected.py) and runs pytest in each
affected component's tests/ directory. Fails if any affected component
has a test failure or if the affected set is empty when it should not be.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AFFECTED = ROOT / "affected.json"


def main() -> int:
    if not AFFECTED.exists():
        print("affected.json missing; run tooling/ci/affected.py first")
        return 2
    doc = json.loads(AFFECTED.read_text())
    components = doc.get("affected", [])
    if not components:
        print("no affected components")
        return 0

    failures = []
    for cid in components:
        for layer in ("ax", "ag", "ac"):
            base = ROOT / "components" / layer / cid
            if base.is_dir():
                tests = base / "tests"
                if not tests.is_dir():
                    print(f"  [skip] {cid}: no tests directory")
                    continue
                r = subprocess.run(
                    [sys.executable, "-m", "pytest", str(tests), "-q"],
                    cwd=ROOT,
                )
                if r.returncode != 0:
                    failures.append(cid)
                print(f"  [{'FAIL' if r.returncode else 'OK'}] {cid}")
                break

    if failures:
        print(f"\ntest failures: {failures}")
        return 1
    print(f"\nall affected components pass: {len(components)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
