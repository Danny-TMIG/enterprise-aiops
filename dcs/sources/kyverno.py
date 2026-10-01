"""Kyverno source — PolicyReport CRDs from `kubectl get polr -A -o json`."""

from __future__ import annotations

from dcs.sources import Attestation, B, meet, source
from dcs.sources._file import read_json

REQ = "DCS-SD-001"  # allowlist / policy — closest fit


@source(REQ)
def kyverno_policyreports() -> Attestation:
    data, err = read_json("DCS_KYVERNO_JSON", REQ, "kyverno")
    if err:
        return err
    if data is None:
        return Attestation(REQ, B.U, "kyverno", "no data")
    items = data.get("items", []) if isinstance(data, dict) else data
    if not items:
        return Attestation(REQ, B.U, "kyverno", "no PolicyReports")

    results: list[tuple[str, B]] = []
    for report in items:
        for r in report.get("results") or []:
            name = r.get("policy", "?") + "/" + r.get("rule", "?")
            result = r.get("result", "").lower()
            if result == "pass":
                results.append((name, B.T))
            elif result == "fail":
                results.append((name, B.F))
            else:  # skip / error / warn
                results.append((name, B.U))

    folded = results[0][1]
    for _, s in results[1:]:
        folded = meet(folded, s)
    fails = [n for n, s in results if s == B.F]
    return Attestation(
        REQ,
        folded,
        "kyverno",
        f"{len(results)} policy results, {len(fails)} fail",
        {"failures": fails[:10]},
    )
