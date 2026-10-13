"""Eval report source — attestations from eval JSON.

Reads DCS_EVAL_JSON (lm-eval-harness or generic shape). Missing -> U.
"""
from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
import os  # pragma: no cover
from pathlib import Path  # pragma: no cover

from dcs.sources import Attestation, B, source  # pragma: no cover

REQ_ACC = "AIG-ACC-001"


def _load() -> dict | None:  # pragma: no cover
    p = os.environ.get("DCS_EVAL_JSON")
    if not p:  # pragma: no cover
        for candidate in ("./ai-governance/evals.json", "./evals.json"):
            if Path(candidate).exists():  # pragma: no cover
                p = candidate
                break
    if not p:  # pragma: no cover
        return None  # pragma: no cover
    try:
        return json.loads(Path(p).read_text())  # pragma: no cover
    except Exception:  # pragma: no cover
        return None  # pragma: no cover


@source(REQ_ACC)
def accuracy_reported() -> Attestation:  # pragma: no cover
    d = _load()
    if d is None:  # pragma: no cover
        return Attestation(REQ_ACC, B.U, "eval_report", "no eval JSON found")  # pragma: no cover
    results = d.get("results", d.get("benchmarks", {}))
    if not results:  # pragma: no cover
        return Attestation(REQ_ACC, B.F, "eval_report", "no benchmarks in report")  # pragma: no cover
    n = len(results) if isinstance(results, (list, dict)) else 0
    return Attestation(  # pragma: no cover
        REQ_ACC, B.T, "eval_report", f"{n} benchmark(s)",
        {"count": n, "keys": list(results)[:5] if isinstance(results, dict) else []},
    )
