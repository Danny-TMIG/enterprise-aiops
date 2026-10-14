#!/usr/bin/env python3
"""Independent verification of the sovereign ledger."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make this script runnable as `python3 sovereign/verify.py` without
# requiring the repo root on PYTHONPATH.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sovereign.ledger import Ledger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, nargs="?", default=Path("sovereign/ledger.jsonl"))
    args = ap.parse_args()

    if not args.path.exists():
        print(f"ledger not found: {args.path}", file=sys.stderr)
        return 2

    checked, valid, errors = Ledger(args.path).verify()
    print(f"ledger:  {args.path}")
    print(f"checked: {checked}")
    print(f"valid:   {valid}")
    print(f"errors:  {len(errors)}")
    for e in errors[:20]:
        print(f"  {e}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
