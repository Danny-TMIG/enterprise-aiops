#!/usr/bin/env python3
"""init_workbook.py — create one decision record per gating decision ID.

Reads catalog/spec_manifest.json. Every open_decisions ID referenced by any
component gets a record under decisions/<id>.json with status OPEN and the
list of components it gates. Content fields are empty; a reviewer fills them.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "catalog" / "spec_manifest.json"
DECISIONS = ROOT / "decisions"


def main() -> int:
    doc = json.loads(MANIFEST.read_text())
    components = doc.get("components", [])

    gating: dict[str, list[str]] = {}
    for c in components:
        for d in c.get("open_decisions", []) or []:
            gating.setdefault(d, []).append(c["id"])

    DECISIONS.mkdir(parents=True, exist_ok=True)
    written = 0
    for did, cids in sorted(gating.items()):
        path = DECISIONS / f"{did}.json"
        if path.exists():
            continue
        record = {
            "decision_id": did,
            "status": "OPEN",
            "title": "UNDECIDED",
            "question": "UNDECIDED",
            "options": [],
            "selected": "UNDECIDED",
            "rationale": "UNDECIDED",
            "closed_by": "UNDECIDED",
            "closed_at": "UNDECIDED",
            "gates_components": sorted(cids),
        }
        payload = json.dumps(record, sort_keys=True).encode("utf-8")
        record["record_seal"] = hashlib.sha256(payload).hexdigest()
        path.write_text(json.dumps(record, indent=2))
        written += 1

    print(f"decisions written: {written}")
    print(f"total decisions in workbook: {len(list(DECISIONS.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
