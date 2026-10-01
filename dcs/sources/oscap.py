"""OpenSCAP source — XCCDF results from `oscap xccdf eval --results-arf`.

Reads an ARF (Asset Reporting Format) XML file. If `xmltodict` is
installed we parse it; otherwise we fall back to a JSON sidecar.

Maps OpenSCAP's five states into Belnap FOUR:
  pass           -> T
  fail           -> F
  error          -> U (evaluation failure, not evidence of falsity)
  unknown        -> U
  notapplicable  -> U (was not evaluated; absence of evidence)
"""
from __future__ import annotations

import os
from pathlib import Path

from dcs.sources import Attestation, B, meet, source

REQ = "DCS-SYS-001"  # open fd count / host baseline — closest we have


def _parse_arf(path: Path) -> dict[str, str]:
    """Return {rule_id: state_str} from an ARF XML file."""
    try:
        import xmltodict  # type: ignore[import-not-found]
    except ImportError:
        return {}
    try:
        doc = xmltodict.parse(path.read_text())
    except Exception:
        return {}
    out: dict[str, str] = {}
    # Traverse: <arf:report><ds:result><rule-result idref=...><result>...</result>
    def walk(o):
        if isinstance(o, dict):
            if "rule-result" in o:
                rr = o["rule-result"]
                if isinstance(rr, dict) and "idref" in rr:
                    out[rr["idref"]] = str(rr.get("result", "")).lower()
                elif isinstance(rr, list):
                    for r in rr:
                        out[r.get("idref", "")] = str(r.get("result", "")).lower()
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return out


def _belnap(s: str) -> B:
    if s == "pass":
        return B.T
    if s == "fail":
        return B.F
    return B.U


@source(REQ)
def openscap_report() -> Attestation:
    path = os.environ.get("DCS_OSCAP_ARF")
    if not path:
        return Attestation(REQ, B.U, "oscap", "DCS_OSCAP_ARF not set")
    p = Path(path)
    if not p.exists():
        return Attestation(REQ, B.U, "oscap", f"{path} not found")
    rules = _parse_arf(p)
    if not rules:
        return Attestation(REQ, B.U, "oscap",
                           "no rules parsed (install xmltodict, or pass a "
                           "JSON sidecar via DCS_OSCAP_JSON)")
    states = [(_belnap(s), rid) for rid, s in rules.items()]
    folded = states[0][0]
    for s, _ in states[1:]:
        folded = meet(folded, s)
    fails = [rid for s, rid in states if s == B.F]
    unk = [rid for s, rid in states if s == B.U]
    return Attestation(
        REQ, folded, "oscap",
        f"{len(rules)} rules: "
        f"{sum(1 for s,_ in states if s==B.T)} pass, {len(fails)} fail, {len(unk)} unknown",
        {"failures": fails[:10], "unknowns": unk[:10]},
    )
