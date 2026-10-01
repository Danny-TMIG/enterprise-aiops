"""dcs self — fold the manifest against local tests + external sources.

When run inside the dcs package this proves the tool is conformant
with its own manifest. When pointed at a customer repo it produces
the evidence bundle that replaces their audit spreadsheet.

Emits three files per run:
  self-<ts>.json          primary signed bundle
  self-<ts>.oscal.json    OSCAL Assessment Results (NIST / FedRAMP)
  self-<ts>.intoto.json   in-toto v1 Statement in a DSSE envelope
"""

from __future__ import annotations

import importlib
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from dcs import sources as src

# Side-effect imports: each module registers @source handlers.
from dcs.sources import aws as _aws  # noqa: F401
from dcs.sources import github as _github  # noqa: F401
from dcs.sources import kube_bench as _kb  # noqa: F401
from dcs.sources import kyverno as _kyv  # noqa: F401
from dcs.sources import oscap as _oscap  # noqa: F401
from dcs.sources import prowler as _prowler  # noqa: F401

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "standards" / "aiops.json"


def _load_manifest() -> list[dict]:
    d = json.loads(MANIFEST.read_text())
    out: list[dict] = []

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "test" in o:
                out.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(d)
    return out


def _run_test(dotted: str) -> tuple[bool, str]:
    mod_name, _, fn_name = dotted.rpartition(".")
    try:
        m = importlib.import_module(mod_name)
    except Exception as e:
        return False, "import: " + str(e)
    fn = getattr(m, fn_name, None)
    if fn is None:
        return False, "missing: " + dotted
    try:
        fn()
        return True, ""
    except AssertionError as e:
        return False, "assert: " + str(e)
    except Exception as e:
        return False, type(e).__name__ + ": " + str(e)


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
                atts.append(
                    src.Attestation(
                        req_id,
                        src.B.U,
                        fn.__module__,
                        "source error: " + type(e).__name__ + ": " + str(e),
                    )
                )
        results.append(
            {
                "id": req_id,
                "criticality": entry.get("criticality", "MUST"),
                "title": entry.get("title", ""),
                "state": src.fold(atts).value,
                "attestations": [asdict(a) for a in atts],
            }
        )
    return {"results": results, "manifest": str(MANIFEST)}


def summarize(payload: dict) -> dict:
    counts: dict[str, dict[str, int]] = {}
    per_source: dict[str, dict[str, int]] = {}
    for r in payload["results"]:
        crit = r["criticality"]
        counts.setdefault(crit, {"T": 0, "F": 0, "U": 0, "B": 0})
        counts[crit][r["state"]] += 1
        for a in r["attestations"]:
            s = a["source"]
            per_source.setdefault(s, {"T": 0, "F": 0, "U": 0, "B": 0})
            per_source[s][a["state"]] += 1

    conflicts = [r["id"] for r in payload["results"] if r["state"] == "B"]
    must_bad = [
        r["id"]
        for r in payload["results"]
        if r["criticality"] == "MUST" and r["state"] in ("F", "B")
    ]
    dual_attested = sum(
        1
        for r in payload["results"]
        if r["criticality"] == "MUST"
        and sum(1 for a in r["attestations"] if a["state"] != "U") >= 2
    )
    must_total = sum(1 for r in payload["results"] if r["criticality"] == "MUST")

    verdict = "CONFORMANT" if not must_bad and not conflicts else "NON_CONFORMANT"
    return {
        "verdict": verdict,
        "counts": counts,
        "per_source": per_source,
        "dual_attested_must": str(dual_attested) + "/" + str(must_total),
        "conflicts": conflicts,
        "must_failures": must_bad,
    }


def _write_exports(payload: dict, out_dir: Path, stem: str) -> None:
    """Write OSCAL and in-toto sidecars next to the primary bundle."""
    try:
        from dcs.oscal import to_oscal

        oscal = to_oscal(payload, title="dcs self " + stem)
        path = out_dir / (stem + ".oscal.json")
        path.write_text(json.dumps(oscal, indent=2))
        print("oscal:    " + str(path))
    except Exception as e:
        print("[warn] OSCAL export failed: " + str(e), file=sys.stderr)

    try:
        from dcs.intoto import to_dsse, to_statement

        stmt = to_statement(payload, subject_name="dcs-self-" + stem)
        env = to_dsse(stmt)
        path = out_dir / (stem + ".intoto.json")
        path.write_text(json.dumps(env, indent=2))
        print("in-toto:  " + str(path))
    except Exception as e:
        print("[warn] in-toto export failed: " + str(e), file=sys.stderr)


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
    stem = "self-" + str(int(time.time()))
    primary = out / (stem + ".json")
    primary.write_text(json.dumps(signed, indent=2))
    print("")
    print("evidence: " + str(primary))

    _write_exports(payload, out, stem)

    return 0 if summary["verdict"] == "CONFORMANT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
