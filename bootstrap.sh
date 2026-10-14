#!/usr/bin/env bash
# ASF Bootstrap — writes README, internal env record, status tool, and tests.
# Idempotent: re-running overwrites the generated files, never duplicates.
set -euo pipefail

REPO="${REPO:-$HOME/aether}"
cd "$REPO"

echo "=============================================================="
echo " ASF BOOTSTRAP"
echo " repo: $REPO"
echo "=============================================================="

# ---------------------------------------------------------------------------
# 1. status.py
# ---------------------------------------------------------------------------
mkdir -p tooling/validation
cat > tooling/validation/status.py <<'STATUS_PY'
#!/usr/bin/env python3
"""Idempotent status report for the Aether repo.

Reads only. Writes nothing. Safe to run any number of times, in any order,
from any working directory, on any machine that has the repo checked out.

Usage:
    python3 tooling/validation/status.py            # summary
    python3 tooling/validation/status.py --json     # machine-readable
    python3 tooling/validation/status.py --gates    # run the six gates too
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

REPORT_FORMAT = "v1"


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parent.parent


ROOT = _repo_root()


def _run(cmd, cwd=None):
    try:
        r = subprocess.run(
            cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=120
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 127, "", str(e)


def git_info() -> dict:
    out = {}
    rc, head, _ = _run(["git", "rev-parse", "HEAD"])
    out["head"] = head if rc == 0 else None
    rc, branch, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    out["branch"] = branch if rc == 0 else None
    rc, remote, _ = _run(["git", "remote", "get-url", "origin"])
    out["remote"] = remote if rc == 0 else None
    rc, status, _ = _run(["git", "status", "--porcelain"])
    out["dirty"] = bool(status)
    out["dirty_files"] = status.splitlines() if status else []
    rc, origin_main, _ = _run(["git", "rev-parse", "origin/main"])
    out["origin_main"] = origin_main if rc == 0 else None
    out["in_sync"] = out["head"] == out.get("origin_main")
    rc, log, _ = _run(["git", "log", "--oneline", "-1"])
    out["last_commit"] = log if rc == 0 else None
    return out


def tree_info() -> dict:
    required = {
        ".github": "dir", "catalog": "dir", "components": "dir",
        "contracts": "dir", "deploy": "dir", "docs": "dir",
        "examples": "dir", "integration": "dir", "libraries": "dir",
        "tooling": "dir", "README.md": "file", "pyproject.toml": "file",
        "Makefile": "file", "LICENSE": "file",
    }
    out = {"required": {}, "missing": []}
    for name, kind in required.items():
        p = ROOT / name
        present = p.is_dir() if kind == "dir" else p.is_file()
        out["required"][name] = present
        if not present:
            out["missing"].append(name)
    layers = {}
    for layer in ("ax", "ag", "ac"):
        d = ROOT / "components" / layer
        layers[layer] = len([x for x in d.iterdir() if x.is_dir()]) if d.is_dir() else 0
    out["components_per_layer"] = layers
    out["components_total"] = sum(layers.values())
    out["components_consistent"] = (
        out["components_total"] == layers["ax"] + layers["ag"] + layers["ac"]
    )
    for d in ("catalog/inventories", "contracts/schemas",
              "docs/architecture", "docs/decisions"):
        out.setdefault("subdirs", {})[d] = (ROOT / d).is_dir()
    out["archive_present"] = (ROOT / "_archive").exists()
    return out


def tracked_info() -> dict:
    rc, files, _ = _run(["git", "ls-files"])
    if rc != 0:
        return {"tracked_files": 0, "tracked_bytes": 0, "size_ok": False}
    flist = files.splitlines()
    total = 0
    missing = 0
    for f in flist:
        try:
            total += (ROOT / f).stat().st_size
        except OSError:
            missing += 1
    return {"tracked_files": len(flist), "tracked_bytes": total,
            "tracked_missing": missing, "size_ok": missing == 0}


def compute_verdict(d: dict) -> dict:
    reasons = []
    g, t, tr = d["git"], d["tree"], d["tracked"]
    if not g["in_sync"]:
        reasons.append({"code": "R2",
            "detail": f"head {g['head']} != origin/main {g['origin_main']}"})
    if g["dirty"]:
        reasons.append({"code": "R3",
            "detail": f"{len(g['dirty_files'])} change(s) in working tree"})
    if not t["components_consistent"]:
        pl = t["components_per_layer"]
        reasons.append({"code": "R4",
            "detail": f"total {t['components_total']} != ax+ag+ac "
                      f"{pl['ax']}+{pl['ag']}+{pl['ac']}"})
    if t["missing"]:
        reasons.append({"code": "R5", "detail": f"missing: {', '.join(t['missing'])}"})
    if t["archive_present"]:
        reasons.append({"code": "R6", "detail": "_archive/ present"})
    if tr.get("tracked_missing", 0) > 0:
        reasons.append({"code": "R7",
            "detail": f"{tr['tracked_missing']} tracked file(s) missing from disk"})
    for gr in d.get("gates", []):
        if not gr["pass"]:
            reasons.append({"code": "R8",
                "detail": f"gate '{gr['name']}' failed (exit {gr['exit']})"})
    return {"status": "OK" if not reasons else "ATTENTION", "reasons": reasons}


GATES = [
    ("orchestrator", [sys.executable, "tooling/master_orchestrator.py"]),
    ("spec_audit",   [sys.executable, "tooling/validation/spec_audit.py"]),
    ("platform_val", [sys.executable, "tooling/validation/platform_validate.py"]),
    ("profiles",     [sys.executable, "tooling/validation/validate_profiles.py"]),
    ("federation",   [sys.executable, "tooling/validation/check_federation_gate.py"]),
    ("tests",        [sys.executable, "-m", "pytest", "tests/", "-q"]),
    ("e2e",          [sys.executable, "integration/e2e/test_full_stack_diagnostic.py"]),
]


def gate_info() -> list:
    results = []
    for name, cmd in GATES:
        rc, stdout, stderr = _run(cmd)
        results.append({"name": name, "pass": rc == 0, "exit": rc,
            "tail": (stdout + ("\n" + stderr if stderr else "")).strip().splitlines()[-4:]})
    return results


def print_human(d: dict) -> None:
    g, t, tr, v = d["git"], d["tree"], d["tracked"], d["verdict"]
    ts = _dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    print("=" * 70)
    print(" AETHER STATUS")
    print(f" report format   : {REPORT_FORMAT}")
    print(f" generated at    : {ts}")
    print("=" * 70)
    print("\nGIT")
    print(f"  branch           : {g['branch']}")
    print(f"  head             : {g['head']}")
    print(f"  origin/main      : {g['origin_main']}")
    print(f"  in sync          : {g['in_sync']}")
    print(f"  remote           : {g['remote']}")
    n = len(g["dirty_files"])
    print(f"  working tree     : {'clean' if not g['dirty'] else str(n) + ' change(s)'}")
    print(f"  last commit      : {g['last_commit']}")
    print("\nTREE")
    pl = t["components_per_layer"]
    print(f"  components       : {t['components_total']}  "
          f"(ax={pl['ax']} ag={pl['ag']} ac={pl['ac']})")
    print(f"  _archive present : {t['archive_present']}")
    miss = t["missing"]
    print(f"  required dirs    : {'all present' if not miss else 'MISSING: ' + str(miss)}")
    for k, val in t.get("subdirs", {}).items():
        print(f"  {k:24s}: {'present' if val else 'MISSING'}")
    print("\nSIZE")
    print(f"  tracked files    : {tr['tracked_files']}")
    print(f"  tracked bytes    : {tr['tracked_bytes']:,}  "
          f"({tr['tracked_bytes']/1024/1024:.2f} MiB)")
    if "gates" in d:
        print("\nGATES")
        for gr in d["gates"]:
            mark = "PASS" if gr["pass"] else "FAIL"
            print(f"  [{mark}] {gr['name']} (exit {gr['exit']})")
            if not gr["pass"]:
                for line in gr["tail"]:
                    print(f"        {line}")
    print()
    if v["status"] == "OK":
        print("VERDICT: OK")
    else:
        codes = ",".join(r["code"] for r in v["reasons"])
        print(f"VERDICT: ATTENTION ({codes})")
        for r in v["reasons"]:
            print(f"  {r['code']}: {r['detail']}")
    print("=" * 70)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gates", action="store_true")
    args = ap.parse_args()
    d = {
        "git": git_info(), "tree": tree_info(), "tracked": tracked_info(),
        "report_format": REPORT_FORMAT,
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if args.gates:
        d["gates"] = gate_info()
    d["verdict"] = compute_verdict(d)
    print(json.dumps(d, indent=2, sort_keys=True)) if args.json else print_human(d)
    return 0 if d["verdict"]["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
STATUS_PY
chmod +x tooling/validation/status.py
echo "[1/4] wrote tooling/validation/status.py"

# ---------------------------------------------------------------------------
# 2. README.md
# ---------------------------------------------------------------------------
cat > README.md <<'README_MD'
# Aether Sovereign Fabric

AI orchestration and coordination platform with verifiable evidence at every step.

## What this repository is

The Aether Sovereign Fabric (ASF) is an AI orchestration and coordination platform. It lets you declare, govern, and execute multi-agent cognitive workflows with verifiable evidence at every step — from a proposed request, through authorization, to physical execution, and back to a verified, auditable outcome. It is not a model, an agent framework, or a chat wrapper. It is the coordination substrate that sits between human intent and machine realization, and its defining property is that no component may grant itself the authority owned by another. Cognition proposes. Govern authorizes. Compute realizes. Evidence returns to Govern before any result becomes a verified governed outcome.

Concretely, the platform enables you to **propose** cognitive work — reasoning, planning, retrieval, and evaluation over authorized knowledge and state; **authorize** consequential action — identity, authority, policy, information flow, capability eligibility, and human approval, all resolved before anything runs; **realize** authorized work — resource qualification, scheduling, execution, recovery, and evidence return; **verify** every terminal outcome through an immutable, reconstructible evidence chain linking intent to result; and **preserve continuity** — cognitive state and memory are typed, versioned, provenance-bearing, and distinct from prompts, context windows, caches, model weights, or execution state. Memory is not automatically truth. Reasoning may combine neural, symbolic, numerical, search, proof, simulation, retrieval, or hybrid methods. Failure, uncertainty, contradiction, denial, abstention, degradation, and incomplete evidence all remain visible rather than being smoothed over.

The repository implements **150 components** across three layers — Cognition (`ax=42`), Govern (`ag=48`), and Compute (`ac=60`). These realize the **75 logical components** defined in the three FAS v1.0 specifications (Cognition 21, Govern 24, Compute 30). The difference reflects implementation decomposition: one logical component may be realized as several concrete modules, and the tree count reflects what is actually present, not what the architecture requires. Both numbers are meaningful and both should be cited — 75 for the architecture, 150 for the tree.

Every object crossing a layer boundary carries the **ASF Common Envelope**, containing schema version, object identity, correlation and causation, cognitive identity and workspace references, sovereign-domain and tenant context, issuer, purpose, classification, event and validity time, provenance, integrity, and evidence references. Canonical schemas live at `40_CROSS_STACK_INTEGRATION/05_Canonical_Schemas` and take precedence over local names whenever an object crosses a layer boundary. Internal projections may add implementation detail but may not expand authority, weaken classification, remove evidence obligations, or alter failure semantics.

Cross-layer behavior is governed by a fixed boundary contract set: `AuthorizationRequest` and `AuthorizationDecision` for authority; `InformationFlowRequest` and `InformationFlowDecision` for disclosure; `CapabilityRequest` resolving to `GovernedCapabilitySet`; `ExecutionOrder` as the sole Govern-to-Compute command; `ExecutionStatus`, `ExecutionResult`, and `ExecutionEvidence` returned to Govern; `GovernedOutcome` and `CognitiveStateUpdateDirective` for closure; and `ApprovalRequest`, `CancellationRevocationDirective`, and `ASFError` as mandatory control objects.

Every retry uses a stable idempotency key. Expired, revoked, malformed, unsupported, unsigned, or context-inconsistent objects fail closed for consequential action. Cancellation and revocation remain observable state transitions and cannot be represented as ordinary execution failure. The producer owns semantic validity at emission; the consumer independently validates before acting.

## Getting started

**1. Clone the repository.** The ASF repository is hosted on GitHub at `Danny-TMIG/Aether-Fabric-Soverign-V1.0`. Clone it into `~/aether` (or any directory you prefer) and change into it. The clone is a standard git checkout; no submodules, no LFS, no external assets are required.

```bash
git clone https://github.com/Danny-TMIG/Aether-Fabric-Soverign-V1.0.git ~/aether
cd ~/aether
