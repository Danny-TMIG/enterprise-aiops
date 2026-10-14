#!/usr/bin/env python3
"""close_federation_gate.py — set federation_status = "active" once the gate
is satisfied. Idempotent. Refuses if any gate item is unmet.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FED = ROOT / "deploy/profiles/enterprise-multidepartment/federation.json"
CHECKER = ROOT / "tooling/check_federation_gate.py"


def main() -> int:
    # Run checker first; if it fails, refuse.
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
    print(r.stdout, end="")
    if r.returncode != 0:
        print("refusing to flip: gate unmet")
        return 1

    fed = json.loads(FED.read_text())
    if fed.get("federation_status") == "active":
        print("federation_status already 'active'")
        return 0

    fed["federation_status"] = "active"
    fed["activated_at"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    FED.write_text(json.dumps(fed, indent=2) + "\n")
    print("federation_status -> 'active'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
