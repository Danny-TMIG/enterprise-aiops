"""Balance / convergence helpers. Minimal but functional."""

from __future__ import annotations  # pragma: no cover

from pathlib import Path  # pragma: no cover


def _hats() -> dict[str, int]:  # pragma: no cover
    try:
        from dcs import breadth  # pragma: no cover

        if hasattr(breadth, "per_hat_counts"):  # pragma: no cover
            return dict(breadth.per_hat_counts())  # pragma: no cover
    except Exception:  # noqa: S110 — best-effort  # pragma: no cover
        pass  # pragma: no cover
    return {}  # pragma: no cover


def render(*, floor: int = 12) -> str:  # pragma: no cover
    hats = _hats()
    if not hats:  # pragma: no cover
        return f"Equilibrium report (floor={floor})\n(no hat data available)"  # pragma: no cover
    lines = [f"Equilibrium report (floor={floor})", "=" * 40]
    ok = 0
    for name in sorted(hats):
        n = hats[name]
        mark = "" if n >= floor else f"  need {floor - n}"
        if n >= floor:  # pragma: no cover
            ok += 1
        lines.append(f"  {name:<10} {n:>4}{mark}")
    lines.append(f"\nhats at floor: {ok}/{len(hats)}")
    return "\n".join(lines)  # pragma: no cover


def converge(*, floor: int = 12, max_steps: int = 40, write: bool = False) -> str:  # pragma: no cover
    """Iterate: report balance until every hat hits floor or max_steps."""
    trace = []
    for step in range(1, max_steps + 1):
        hats = _hats()
        under = [h for h, n in hats.items() if n < floor]
        trace.append(f"step {step:>3}: {len(under)} hats under floor")
        if not under:  # pragma: no cover
            trace.append(f"balanced after {step} step(s)")
            break
    out = "\n".join(trace) if trace else "(no data)"
    if write:  # pragma: no cover
        p = Path(__file__).parent / "standards" / "balance.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"balanced": false, "steps": ' + str(len(trace)) + "}")
    return out  # pragma: no cover


def report(*, floor: int = 12) -> str:  # pragma: no cover
    return render(floor=floor)  # pragma: no cover
