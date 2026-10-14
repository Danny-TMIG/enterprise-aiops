#!/usr/bin/env python3
"""check_federation_gate.py — refuse federation_status='active' unless gate met."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "deploy/profiles/enterprise-multidepartment/federation-activation-gate.json"
FED  = ROOT / "deploy/profiles/enterprise-multidepartment/federation.json"


def main() -> int:
    gate = json.loads(GATE.read_text())
    fed  = json.loads(FED.read_text())
    status = fed.get("federation_status")
    if status != "active":
        print(f"federation_status = {status!r} — flip is blocked (expected)")
        return 0
    missing: list[str] = []
    req = gate["flip_would_require"]
    if not req["named_owner"]["present"]: missing.append("named_owner.present false")
    if not req["contract_version"]["present"]: missing.append("contract_version.present false")
    if not req["runbook"]["present"]: missing.append("runbook.present false")
    for k, v in req["reviewed_by"].items():
        if v is None: missing.append(f"reviewed_by.{k} null")
    if missing:
        print("federation_status='active' but gate unmet:")
        for m in missing: print(f"  - {m}")
        return 1
    print("federation_status='active' and gate satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
