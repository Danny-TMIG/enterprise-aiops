"""Human-readable renderings."""

from dcs.triad.lattice import ALL_STATES  # pragma: no cover
from dcs.triad.laws import run_all  # pragma: no cover


def lattice_diagram() -> str:  # pragma: no cover
    lines = ["Belnap FOUR — verification lattice", "=" * 44]
    for s in ALL_STATES:
        lines.append(f"  {s.name:<9} t={s.t}  f={s.f}")
    lines.append("")
    lines.append("Truth order:      FAIL < UNKNOWN,CONFLICT < PASS")
    lines.append("Knowledge order:  UNKNOWN < PASS,FAIL < CONFLICT")
    lines.append("")
    lines.append("Operations:  meet_truth=AND  join_truth=OR")
    lines.append("             join_know=union of information")
    lines.append("             meet_know=common information")
    return "\n".join(lines)  # pragma: no cover


def law_report() -> str:  # pragma: no cover
    results = run_all()
    lines = ["Algebraic laws", "=" * 44]
    for name, ok in results.items():
        lines.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
    n_ok = sum(1 for v in results.values() if v)
    lines.append("")
    lines.append(f"{n_ok}/{len(results)} laws hold")
    return "\n".join(lines)  # pragma: no cover
