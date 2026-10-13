"""kube-bench source — CIS Kubernetes Benchmark results."""

from __future__ import annotations  # pragma: no cover

from dcs.sources import Attestation, B, meet, source  # pragma: no cover
from dcs.sources._file import read_json  # pragma: no cover

REQ = "DCS-NWE-001"


@source(REQ)
def kube_bench_report() -> Attestation:  # pragma: no cover
    data, err = read_json("DCS_KUBE_BENCH_JSON", REQ, "kube-bench")
    if err:  # pragma: no cover
        return err  # pragma: no cover
    if data is None:  # pragma: no cover
        return Attestation(REQ, B.U, "kube-bench", "no data")  # pragma: no cover
    if not isinstance(data, dict):  # pragma: no cover
        return Attestation(REQ, B.U, "kube-bench", "unexpected root type")  # pragma: no cover

    results: list[tuple[str, B]] = []
    for section in data.get("Controls", []) or []:
        for test in section.get("tests", []) or []:
            state = test.get("state", "").upper()
            rid = test.get("test_number", "")
            if state == "PASS":  # pragma: no cover
                results.append((rid, B.T))
            elif state == "FAIL":
                results.append((rid, B.F))
            else:
                results.append((rid, B.U))

    if not results:  # pragma: no cover
        return Attestation(REQ, B.U, "kube-bench", "no results in JSON")  # pragma: no cover
    folded = results[0][1]
    for _, s in results[1:]:
        folded = meet(folded, s)
    fails = [rid for rid, s in results if s == B.F]
    return Attestation(  # pragma: no cover
        REQ,
        folded,
        "kube-bench",
        f"{len(results)} tests, {len(fails)} fail",
        {"failures": fails[:10]},
    )
