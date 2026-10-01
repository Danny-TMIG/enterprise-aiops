"""Human-readable renderings."""
import json
from dcs.mesh.taxonomy import FAMILIES, AXIS_OF
from dcs.mesh.ucs import UCS, UCS_STAGES
from dcs.mesh.laws import run_all


def family_table() -> str:
    lines = ["MESH — six behavior families", "=" * 60]
    for fam, body in FAMILIES.items():
        stages = body["stages"]
        axis = AXIS_OF[fam]
        lines.append(f"  {fam}  {body['title']:<12}  "
                     f"{len(stages):>3} stages  axis={axis}")
    lines.append("")
    lines.append("  G Generator   C Compiler   R Resolver")
    lines.append("  D Daemon      B Binary     K Kernel")
    return "\n".join(lines)


def ucs_diagram() -> str:
    lines = ["UCS — universal construction pipeline", "=" * 60]
    lines.append(f"  {len(UCS)} stages")
    lines.append("")
    for sid, label in UCS_STAGES:
        lines.append(f"  {sid:<4} {label}")
    lines.append("")
    lines.append("  spec → IR → synthesize → build → verify → publish → self-evolve")
    return "\n".join(lines)


def law_report() -> str:
    results = run_all()
    lines = ["Pipeline algebra laws", "=" * 60]
    for name, ok in results.items():
        lines.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
    n_ok = sum(1 for v in results.values() if v)
    lines.append("")
    lines.append(f"{n_ok}/{len(results)} laws hold")
    return "\n".join(lines)


def verify_report() -> str:
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
    return json.dumps(payload, indent=2)
