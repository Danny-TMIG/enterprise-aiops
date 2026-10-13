"""Human-readable renderings."""

import json  # pragma: no cover

from dcs.mesh.laws import run_all  # pragma: no cover
from dcs.mesh.taxonomy import AXIS_OF, FAMILIES  # pragma: no cover
from dcs.mesh.ucs import UCS, UCS_STAGES  # pragma: no cover


def family_table() -> str:  # pragma: no cover
    lines = ["MESH — six behavior families", "=" * 60]
    for fam, body in FAMILIES.items():
        stages = body["stages"]
        axis = AXIS_OF[fam]
        lines.append(f"  {fam}  {body['title']:<12}  {len(stages):>3} stages  axis={axis}")
    lines.append("")
    lines.append("  G Generator   C Compiler   R Resolver")
    lines.append("  D Daemon      B Binary     K Kernel")
    return "\n".join(lines)  # pragma: no cover


def ucs_diagram() -> str:  # pragma: no cover
    lines = ["UCS — universal construction pipeline", "=" * 60]
    lines.append(f"  {len(UCS)} stages")
    lines.append("")
    for sid, label in UCS_STAGES:
        lines.append(f"  {sid:<4} {label}")
    lines.append("")
    lines.append("  spec → IR → synthesize → build → verify → publish → self-evolve")
    return "\n".join(lines)  # pragma: no cover


def law_report() -> str:  # pragma: no cover
    results = run_all()
    lines = ["Pipeline algebra laws", "=" * 60]
    for name, ok in results.items():
        lines.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
    n_ok = sum(1 for v in results.values() if v)
    lines.append("")
    lines.append(f"{n_ok}/{len(results)} laws hold")
    return "\n".join(lines)  # pragma: no cover


def verify_report() -> str:  # pragma: no cover
    t, r = UCS.verify()
    payload = {
        "pipeline": UCS.name,
        "length": len(UCS),
        "triad": t.to_dict(),
        "verdict": t.verdict(),
        "digest": r.digest,
        "signature": r.signature[:16] + "...",
        "receipt_check": __import__("dcs.triad", fromlist=["Kernel"]).Kernel().check(r),
    }
    return json.dumps(payload, indent=2)  # pragma: no cover
