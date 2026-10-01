"""dcs self — fold the manifest against local tests + external sources.

When run inside the dcs package, this proves the tool is conformant
with its own manifest. When pointed at a customer repo, it produces
the evidence bundle that replaces their audit spreadsheet.
"""
from __future__ import annotations

import importlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from dcs import sources as src

# Side-effect imports: each module registers @source handlers.
from dcs.sources import github as _github  # noqa: F401

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "standards" / "aiops.json"


def _load_manifest() -> list[dict]:
    d = json.loads(MANIFEST.read_text())
    out: list[dict] = []
    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "test" in o:
                out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d)
    return out


def _run_test(dotted: str) -> tuple[bool, str]:
    mod_name, _, fn_name = dotted.rpartition(".")
    try:
        m = importlib.import_module(mod_name)
    except Exception as e:
        return False, f"import: {e}"
    fn = getattr(m, fn_name, None)
    if fn is None:
        return False, f"missing: {dotted}"
    try:
        fn()
        return True, ""
    except AssertionError as e:
        return False, f"assert: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _local(req_id: str, dotted: str) -> src.Attestation:
    ok, reason = _run_test(dotted)
    return src.Attestation(
        req_id=req_id,
        state=src.B.T if ok else src.B.F,
        source="local",
        reason=reason,
        evidence={"test": dotted},
    )


def run() -> dict:
    results = []
    for entry in _load_manifest():
        req_id = entry["id"]
        atts = [_local(req_id, entry["test"])]
        for fn in src.sources_for(req_id):
            try:
                atts.append(fn())
            except Exception as e:
                atts.append(src.Attestation(
                    req_id, src.B.U, fn.__module__,
                    f"source error: {type(e).__name__}: {e}",
                ))
        results.append({
            "id": req_id,
            "criticality": entry.get("criticality", "MUST"),
            "title": entry.get("title", ""),
            "state": src.fold(atts).value,
            "attestations": [asdict(a) for a in atts],
        })
    return {"results": results, "manifest": str(MANIFEST)}


def summarize(payload: dict) -> dict:
    counts: dict[str, dict[str, int]] = {}
    per_source: dict[str, dict[str, int]] = {}
    for r in payload["results"]:
        crit = r["criticality"]
        counts.setdefault(crit, {"T": 0, "F": 0, "U": 0, "B": 0})
        counts[crit][r["state"]] += 1
        for a in r["attestations"]:
            src = a["source"]
            per_source.setdefault(src, {"T": 0, "F": 0, "U": 0, "B": 0})
            per_source[src][a["state"]] += 1

    conflicts = [r["id"] for r in payload["results"] if r["state"] == "B"]
    must_bad = [r["id"] for r in payload["results"]
                if r["criticality"] == "MUST" and r["state"] in ("F", "B")]

    # dual-attested = MUST requirements with at least 2 non-U attestations
    dual_attested = sum(
        1 for r in payload["results"]
        if r["criticality"] == "MUST"
        and sum(1 for a in r["attestations"] if a["state"] != "U") >= 2
    )
    must_total = sum(1 for r in payload["results"] if r["criticality"] == "MUST")

    verdict = "CONFORMANT" if not must_bad and not conflicts else "NON_CONFORMANT"
    return {
        "verdict": verdict,
        "counts": counts,
        "per_source": per_source,
        "dual_attested_must": f"{dual_attested}/{must_total}",
        "conflicts": conflicts,
        "must_failures": must_bad,
    }


def main() -> int:
    payload = run()
    summary = summarize(payload)
    print(json.dumps(summary, indent=2))

    bundle = {
        "kind": "dcs.self",
        "manifest": payload["manifest"],
        "results": payload["results"],
        "verdict": summary["verdict"],
    }
    try:
        from dcs.signing import sign_bundle
        signed = sign_bundle(bundle)
    except Exception:
        signed = bundle

    out = ROOT / "evidence"
    out.mkdir(exist_ok=True)
    path = out / f"self-{int(time.time())}.json"
    path.write_text(json.dumps(signed, indent=2))
    print(f"\nevidence: {path}")
    return 0 if summary["verdict"] == "CONFORMANT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
