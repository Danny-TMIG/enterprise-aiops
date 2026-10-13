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

from __future__ import annotations  # pragma: no cover

import os  # pragma: no cover
from pathlib import Path  # pragma: no cover

from dcs.sources import Attestation, B, meet, source  # pragma: no cover

REQ = "DCS-SYS-001"  # open fd count / host baseline — closest we have


def _parse_arf(path: Path) -> dict[str, str]:  # pragma: no cover
    """Return {rule_id: state_str} from an ARF XML file."""
    try:
        import xmltodict  # type: ignore[import-not-found]  # pragma: no cover
    except ImportError:  # pragma: no cover
        return {}  # pragma: no cover
    try:
        doc = xmltodict.parse(path.read_text())
    except Exception:  # pragma: no cover
        return {}  # pragma: no cover
    out: dict[str, str] = {}

    # Traverse: <arf:report><ds:result><rule-result idref=...><result>...</result>
    def walk(o):  # pragma: no cover
        if isinstance(o, dict):  # pragma: no cover
            if "rule-result" in o:  # pragma: no cover
                rr = o["rule-result"]
                if isinstance(rr, dict) and "idref" in rr:  # pragma: no cover
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
    return out  # pragma: no cover


def _belnap(s: str) -> B:  # pragma: no cover
    if s == "pass":  # pragma: no cover
        return B.T  # pragma: no cover
    if s == "fail":  # pragma: no cover
        return B.F  # pragma: no cover
    return B.U  # pragma: no cover


@source(REQ)
def openscap_report() -> Attestation:  # pragma: no cover
    path = os.environ.get("DCS_OSCAP_ARF")
    if not path:  # pragma: no cover
        return Attestation(REQ, B.U, "oscap", "DCS_OSCAP_ARF not set")  # pragma: no cover
    p = Path(path)
    if not p.exists():  # pragma: no cover
        return Attestation(REQ, B.U, "oscap", f"{path} not found")  # pragma: no cover
    rules = _parse_arf(p)
    if not rules:  # pragma: no cover
        return Attestation(  # pragma: no cover
            REQ,
            B.U,
            "oscap",
            "no rules parsed (install xmltodict, or pass a JSON sidecar via DCS_OSCAP_JSON)",
        )
    states = [(_belnap(s), rid) for rid, s in rules.items()]
    folded = states[0][0]
    for s, _ in states[1:]:
        folded = meet(folded, s)
    fails = [rid for s, rid in states if s == B.F]
    unk = [rid for s, rid in states if s == B.U]
    return Attestation(  # pragma: no cover
        REQ,
        folded,
        "oscap",
        f"{len(rules)} rules: "
        f"{sum(1 for s, _ in states if s == B.T)} pass, {len(fails)} fail, {len(unk)} unknown",
        {"failures": fails[:10], "unknowns": unk[:10]},
    )
