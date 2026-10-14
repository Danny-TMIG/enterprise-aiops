#!/usr/bin/env python3
"""closure.py — report which components are unblocked by closed decisions.

A component becomes buildable when every decision in its open_decisions list
has status CLOSED. Writes decisions/buildable.json and prints the list.

Usage:
  python tooling/decisions/closure.py            # report only
  python tooling/decisions/closure.py --check    # fail if any referenced
                                                 # decision file is missing
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "catalog" / "spec_manifest.json"
DECISIONS = ROOT / "decisions"


def load_decisions() -> dict[str, dict]:
    out = {}
    for p in DECISIONS.glob("*.json"):
        try:
            doc = json.loads(p.read_text())
        except Exception:
            continue
        did = doc.get("decision_id")
        if did:
            out[did] = doc
    return out


def main() -> int:
    check = "--check" in sys.argv
    doc = json.loads(MANIFEST.read_text())
    components = doc.get("components", [])
    decisions = load_decisions()

    buildable, blocked, missing = [], [], []
    for c in components:
        gates = c.get("open_decisions", []) or []
        if not gates:
            buildable.append(c["id"])
            continue
        unresolved = []
        for g in gates:
            rec = decisions.get(g)
            if rec is None:
                missing.append((c["id"], g))
                unresolved.append(g)
            elif rec.get("status") != "CLOSED":
                unresolved.append(g)
        if unresolved:
            blocked.append({"component": c["id"], "open": unresolved})
        else:
            buildable.append(c["id"])

    out = {
        "buildable": sorted(buildable),
        "blocked": sorted(blocked, key=lambda x: x["component"]),
        "missing_decision_files": sorted(missing),
    }
    (DECISIONS / "buildable.json").write_text(json.dumps(out, indent=2))

    print(f"buildable components: {len(buildable)}")
    for cid in sorted(buildable):
        print(f"  + {cid}")
    print(f"blocked components:   {len(blocked)}")
    if missing:
        print(f"missing decision files referenced by components: {len(missing)}")
        for cid, did in missing[:20]:
            print(f"  ! {cid} -> {did}")
        if check:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
