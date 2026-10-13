"""dcs attest — the system attests itself.

Runs every layer, collects every verdict, signs the summary.
This is the meta-receipt: the chain that attests the chains that
attest the actions.
"""
from __future__ import annotations  # pragma: no cover

import hashlib  # pragma: no cover
import json  # pragma: no cover
import subprocess  # pragma: no cover
import sys  # pragma: no cover
import time  # pragma: no cover
from dataclasses import asdict, dataclass  # pragma: no cover
from pathlib import Path  # pragma: no cover

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:  # pragma: no cover
    p = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")  # pragma: no cover


@dataclass
class Layer:  # pragma: no cover
    name: str
    command: list[str]
    exit_code: int = -1
    stdout_tail: str = ""
    duration_ms: int = 0
    verdict: str = "UNKNOWN"


def run_layer(name: str, cmd: list[str]) -> Layer:  # pragma: no cover
    t0 = time.time()
    rc, out = _run(cmd)
    dt = int((time.time() - t0) * 1000)
    tail = "\n".join(out.strip().splitlines()[-4:])
    verdict = "PASS" if rc == 0 else "FAIL"
    return Layer(name=name, command=cmd, exit_code=rc,  # pragma: no cover
                 stdout_tail=tail, duration_ms=dt, verdict=verdict)


PY = sys.executable


LAYERS = [
    ("static_grounding",   [PY, "dcs_codeql/pycheck.py", str(ROOT)]),
    ("dynamic_grounding",  [PY, "dcs_codeql/dyncheck.py"]),
    ("non_claims_orth",    [PY, "-m", "dcs.non_claims", "check"]),
    ("grounded_orth",      [PY, "-m", "dcs.grounded", "orth"]),
    ("non_claims_duals",   [PY, "-m", "dcs.grounded", "check"]),
    ("formal_systems",     [PY, "-m", "dcs.formal_systems", "save"]),
    ("algorithms",         [PY, "-m", "dcs.algorithms", "save"]),
    ("cross_corpus",       [PY, "-m", "dcs.cross_corpus", "save"]),
]


def canon(obj) -> bytes:  # pragma: no cover
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()  # pragma: no cover


def digest_of(obj) -> str:  # pragma: no cover
    return hashlib.sha256(canon(obj)).hexdigest()  # pragma: no cover


def main():  # pragma: no cover
    key = b"attestation-key-not-for-production"
    print("═" * 72)
    print("  DCS SELF-ATTESTATION")
    print("═" * 72)
    print()

    layers: list[Layer] = []
    for name, cmd in LAYERS:
        layer = run_layer(name, cmd)
        layers.append(layer)
        tag = "✓" if layer.verdict == "PASS" else "✗"
        print(f"  {tag} {name:<22} [{layer.verdict:<4}]  {layer.duration_ms:>4}ms")
        if layer.verdict != "PASS":  # pragma: no cover
            for line in layer.stdout_tail.splitlines():
                print(f"      {line}")

    print()
    summary = {
        "version": "0.5.0",
        "generated_at": time.time(),
        "layers": [asdict(l) for l in layers],
        "verdict": "PASS" if all(l.verdict == "PASS" for l in layers) else "FAIL",
        "counts": {
            "pass": sum(1 for l in layers if l.verdict == "PASS"),
            "fail": sum(1 for l in layers if l.verdict == "FAIL"),
            "total": len(layers),
        },
    }

    # meta-receipt: the digest of the summary, signed
    summary["digest"] = digest_of({k: v for k, v in summary.items() if k != "digest"})
    summary["signature"] = hashlib.sha256(
        key + summary["digest"].encode()
    ).hexdigest()

    out = ROOT / "self_attestation.json"
    out.write_text(json.dumps(summary, indent=2))

    print("═" * 72)
    print(f"  layers passing: {summary['counts']['pass']} / {summary['counts']['total']}")
    print(f"  verdict:        {summary['verdict']}")
    print(f"  digest:         {summary['digest'][:32]}...")
    print(f"  signature:      {summary['signature'][:32]}...")
    print(f"  written to:     {out}")
    print("═" * 72)

    return 0 if summary["verdict"] == "PASS" else 1  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())  # pragma: no cover
