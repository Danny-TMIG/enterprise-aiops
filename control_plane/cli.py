"""Command-line runner for the A-Z control plane."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from control_plane import PollinationGraph, Runner


def _load_request(path: Path | None) -> dict:
    if path is None:
        return {"input": {}}
    data = json.loads(path.read_text())
    return {"input": data}


def _write_evidence(run_result, request: dict, out: Path) -> None:
    payload = {
        "run_id": str(uuid.uuid4()),
        "issued_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "path": run_result.path,
        "status": run_result.status,
        "halted_at": run_result.halted_at,
        "request_hash_inputs": sorted(request.get("input", {}).keys()),
        "steps": run_result.steps,
        "artifacts": run_result.artifacts,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path,
                    default=Path("contracts/layers/layer-manifest.json"))
    ap.add_argument("--path", required=True,
                    help="layer path, e.g. ABCD or ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ap.add_argument("--request", type=Path, default=None,
                    help="JSON request file; omit for empty input")
    ap.add_argument("--evidence-out", type=Path, default=Path("run-evidence.json"))
    args = ap.parse_args()

    graph = PollinationGraph.from_manifest(args.manifest)
    runner = Runner(graph=graph)
    request = _load_request(args.request)
    result = runner.run(args.path, seed=request.get("input", {}))

    _write_evidence(result, request, args.evidence_out)

    print(f"path: {result.path}")
    print(f"status: {result.status}")
    if result.halted_at:
        print(f"halted_at: {result.halted_at}")
    for step in result.steps:
        if "letter" in step:
            print(f"  {step['letter']} {step['status']:8s} {step.get('artifact', '')}")
        else:
            print(f"  error: {step.get('error')}")
    print(f"artifacts: {len(result.artifacts)}")
    print(f"evidence: {args.evidence_out}")

    return 0 if result.status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
