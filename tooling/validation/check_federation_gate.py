#!/usr/bin/env python3
"""check_federation_gate.py — allow the federation flip only when every gate
item in federation-activation-gate.json is satisfied.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from pathlib import Path as _Path
def _repo_root():
    p = _Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / 'pyproject.toml').exists():
            return parent
    return p.parent.parent
_REPO_ROOT = _repo_root()

ROOT = _REPO_ROOT
GATE = ROOT / "deploy/profiles/enterprise-multidepartment/federation-activation-gate.json"
FED  = ROOT / "deploy/profiles/enterprise-multidepartment/federation.json"


def _present(v) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, dict):
        return bool(v) and v.get("present", True) is not False
    return v is not None


def main() -> int:
    gate = json.loads(GATE.read_text())
    fed  = json.loads(FED.read_text())
    req  = gate["flip_would_require"]
    status = fed.get("federation_status")

    missing: list[str] = []

    owner = req.get("named_owner", {})
    if not _present(owner) or not owner.get("owner"):
        missing.append("named_owner")

    cv = req.get("contract_version", {})
    if not _present(cv) or not cv.get("schema_id"):
        missing.append("contract_version")

    rb = req.get("runbook", {})
    if not _present(rb) or not rb.get("path"):
        missing.append("runbook")
    elif not (ROOT / rb["path"]).exists():
        missing.append(f"runbook (file missing: {rb['path']})")

    for key in ("engineering_review", "security_review", "ops_review"):
        r = req.get("reviewed_by", {}).get(key)
        if not isinstance(r, dict) or r.get("verdict") != "approved":
            missing.append(f"reviewed_by.{key}")

    if missing:
        print(f"federation gate UNMET — {len(missing)} item(s):")
        for m in missing:
            print(f"  - {m}")
        if status == "active":
            print(f"FATAL: federation_status={status!r} but gate is unmet")
            return 1
        print(f"federation_status = {status!r} — flip remains blocked (correct)")
        return 0

    if status != "active":
        print(f"gate satisfied but federation_status = {status!r}")
        print("  run: python3 tooling/close_federation_gate.py")
        return 0

    print(f"federation_status = 'active' and all gate items satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
