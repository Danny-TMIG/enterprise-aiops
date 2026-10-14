#!/usr/bin/env python3
"""close.py — mark a decision CLOSED with content.

Usage:
  python tooling/decisions/close.py <DECISION_ID> \
      --title "..." --question "..." --selected "..." \
      --rationale "..." --closed-by "..."

Reads decisions/<ID>.json, updates the record, recomputes the seal,
and re-runs the closure report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "decisions"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("decision_id")
    ap.add_argument("--title", required=True)
    ap.add_argument("--question", required=True)
    ap.add_argument("--selected", required=True)
    ap.add_argument("--rationale", required=True)
    ap.add_argument("--closed-by", required=True)
    args = ap.parse_args()

    path = DECISIONS / f"{args.decision_id}.json"
    if not path.exists():
        print(f"no such decision record: {path}")
        return 2

    rec = json.loads(path.read_text())
    rec["title"] = args.title
    rec["question"] = args.question
    rec["selected"] = args.selected
    rec["rationale"] = args.rationale
    rec["closed_by"] = args.closed_by
    rec["closed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["status"] = "CLOSED"

    payload = json.dumps(
        {k: v for k, v in rec.items() if k != "record_seal"}, sort_keys=True
    ).encode("utf-8")
    rec["record_seal"] = hashlib.sha256(payload).hexdigest()
    path.write_text(json.dumps(rec, indent=2))

    print(f"closed {args.decision_id}: {args.selected}")
    subprocess.run(
        [sys.executable, str(ROOT / "tooling" / "decisions" / "closure.py")],
        cwd=ROOT,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
