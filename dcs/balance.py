"""Balance / convergence helpers. Minimal but functional."""

from __future__ import annotations

from pathlib import Path


def _hats() -> dict[str, int]:
    try:
        from dcs import breadth

        if hasattr(breadth, "per_hat_counts"):
            return dict(breadth.per_hat_counts())
    except Exception:  # noqa: S110 — best-effort
        pass
    return {}


def render(*, floor: int = 12) -> str:
    hats = _hats()
    if not hats:
        return f"Equilibrium report (floor={floor})\n(no hat data available)"
    lines = [f"Equilibrium report (floor={floor})", "=" * 40]
    ok = 0
    for name in sorted(hats):
        n = hats[name]
        mark = "" if n >= floor else f"  need {floor - n}"
        if n >= floor:
            ok += 1
        lines.append(f"  {name:<10} {n:>4}{mark}")
    lines.append(f"\nhats at floor: {ok}/{len(hats)}")
    return "\n".join(lines)


def converge(*, floor: int = 12, max_steps: int = 40, write: bool = False) -> str:
    """Iterate: report balance until every hat hits floor or max_steps."""
    trace = []
    for step in range(1, max_steps + 1):
        hats = _hats()
        under = [h for h, n in hats.items() if n < floor]
        trace.append(f"step {step:>3}: {len(under)} hats under floor")
        if not under:
            trace.append(f"balanced after {step} step(s)")
            break
    out = "\n".join(trace) if trace else "(no data)"
    if write:
        p = Path(__file__).parent / "standards" / "balance.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"balanced": false, "steps": ' + str(len(trace)) + "}")
    return out


def report(*, floor: int = 12) -> str:
    return render(floor=floor)
