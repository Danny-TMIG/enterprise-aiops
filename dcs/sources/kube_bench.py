"""kube-bench source — CIS Kubernetes Benchmark results."""

from __future__ import annotations

from dcs.sources import Attestation, B, meet, source
from dcs.sources._file import read_json

REQ = "DCS-NWE-001"


@source(REQ)
def kube_bench_report() -> Attestation:
    data, err = read_json("DCS_KUBE_BENCH_JSON", REQ, "kube-bench")
    if err:
        return err
    if data is None:
        return Attestation(REQ, B.U, "kube-bench", "no data")
    if not isinstance(data, dict):
        return Attestation(REQ, B.U, "kube-bench", "unexpected root type")

    results: list[tuple[str, B]] = []
    for section in data.get("Controls", []) or []:
        for test in section.get("tests", []) or []:
            state = test.get("state", "").upper()
            rid = test.get("test_number", "")
            if state == "PASS":
                results.append((rid, B.T))
            elif state == "FAIL":
                results.append((rid, B.F))
            else:
                results.append((rid, B.U))

    if not results:
        return Attestation(REQ, B.U, "kube-bench", "no results in JSON")
    folded = results[0][1]
    for _, s in results[1:]:
        folded = meet(folded, s)
    fails = [rid for rid, s in results if s == B.F]
    return Attestation(
        REQ,
        folded,
        "kube-bench",
        f"{len(results)} tests, {len(fails)} fail",
        {"failures": fails[:10]},
    )
