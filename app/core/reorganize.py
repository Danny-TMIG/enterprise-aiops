"""Self-referential reorganization.

The fabric reads its own ledger and mutates its own capability table.
Three rules, no invention:

    R1  (removed) — the reorganizer never downgrades a `real` claim.
        A wrong `real` is a P6 stability failure; it is fixed by
        implementing the missing registration, not by hiding it.
    R2  a capability marked `aspirational` whose impl is registered
        and whose recent dispatch rate is > 0 gets promoted to `real`
        (the claim was conservative)
    R3  every mutation writes its own event, with the reason, the
        prior value, and the trigger that derived it

The reorganizer is itself a capability (`reorganize`) so its own
operations are subject to R1-R3 on the next pass. Self-referential by
construction, terminating by design: proposals are bounded by what
the ledger contains, and each mutation changes the state that future
proposals derive from.

Dry run by default. Pass apply=True to commit.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


# ── read: the ledger as ground truth ────────────────────────────────
@dataclass
class DispatchStat:
    code: str
    attempts: int = 0
    successes: int = 0
    last_reason: str = ""
    last_seq: int = 0

    @property
    def rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0


@dataclass
class Proposal:
    code: str
    field: str           # "status"
    before: Any
    after: Any
    reason: str
    trigger_seq: int | None = None


@dataclass
class Report:
    read: int = 0
    dispatch_stats: dict[str, DispatchStat] = field(default_factory=dict)
    proposals: list[Proposal] = field(default_factory=list)
    applied: list[Proposal] = field(default_factory=list)
    dry_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "read": self.read,
            "dry_run": self.dry_run,
            "capabilities_seen": len(self.dispatch_stats),
            "proposals": [asdict(p) for p in self.proposals],
            "applied": [asdict(p) for p in self.applied],
        }


def _connect(db: Path = DB) -> sqlite3.Connection:
    con = sqlite3.connect(db, timeout=10.0)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=10000")
    return con


def _read_dispatch_events(con: sqlite3.Connection,
                          window: int = 500) -> dict[str, DispatchStat]:
    stats: dict[str, DispatchStat] = {}
    for seq, payload in con.execute(
        "SELECT seq, payload FROM events "
        "WHERE kind='dispatch' ORDER BY seq DESC LIMIT ?", (window,)
    ):
        try:
            d = json.loads(payload)
        except Exception:
            continue
        code = d.get("code") or d.get("payload", {}).get("code")
        if not code:
            continue
        s = stats.setdefault(code, DispatchStat(code=code))
        s.attempts += 1
        if d.get("ok"):
            s.successes += 1
        elif not s.last_reason:
            s.last_reason = (d.get("reason") or "")[:200]
        if not s.last_seq:
            s.last_seq = seq
    return stats


# ── propose ─────────────────────────────────────────────────────────
def _cap_row(con: sqlite3.Connection, code: str
             ) -> tuple[str, str] | None:
    r = con.execute(
        "SELECT status, home FROM capabilities WHERE code=?", (code,)
    ).fetchone()
    return (r[0], r[1] or "") if r else None


def _has_registered_impl(code: str) -> bool:
    try:
        from app.core import capabilities as c
        c._autoload(code)                       # attempt
        return code in c._IMPL
    except Exception:
        return False


def propose(stats: dict[str, DispatchStat]) -> list[Proposal]:
    out: list[Proposal] = []
    con = _connect()
    for code, s in stats.items():
        row = _cap_row(con, code)
        if not row:
            continue
        status, home = row

        # R2 only: aspirational -> real when an impl is registered and
        # recent dispatches have succeeded. The reorganizer never
        # downgrades a `real` capability; a wrong `real` claim is a
        # P6 stability failure, not something to hide by mutation.
        if status == "aspirational" and s.successes > 0 and _has_registered_impl(code):
            out.append(Proposal(
                code=code, field="status",
                before="aspirational", after="real",
                reason=(f"R2: {s.successes}/{s.attempts} recent dispatches "
                        f"succeeded and impl is registered"),
                trigger_seq=s.last_seq,
            ))
    con.close()
    return out


# ── apply ───────────────────────────────────────────────────────────
def apply_proposals(proposals: list[Proposal],
                    sub: Any) -> list[Proposal]:
    """Mutate the capability table, then close. The ledger write
    happens after the mutation connection is released, so two
    writers never contend for the same lock."""
    applied: list[Proposal] = []
    for p in proposals:
        if p.field != "status":
            continue
        changed = False
        try:
            con = _connect()
            cur = con.execute(
                "UPDATE capabilities SET status=? WHERE code=? AND status=?",
                (p.after, p.code, p.before),
            )
            changed = cur.rowcount > 0
            con.commit()
            con.close()
        except Exception as e:
            # release whatever we have, then log the failure
            try:
                con.close()  # type: ignore[name-defined]
            except Exception:
                pass
            sub.append("reorganize.error", p.code,
                       {"proposal": asdict(p), "error": str(e)})
            continue
        if changed:
            applied.append(p)
            sub.append("reorganize.mutation", p.code, asdict(p))
    return applied


# ── orchestrate ─────────────────────────────────────────────────────
def run(*, apply: bool = False, window: int = 500) -> Report:
    from app.core.ram_substrate import RAMSubstrate
    sub = RAMSubstrate(capacity=4096, autoload=False)

    con = _connect()
    stats = _read_dispatch_events(con, window=window)
    con.close()

    rep = Report(read=len(stats), dispatch_stats=stats, dry_run=not apply)

    proposals = propose(stats)
    rep.proposals = proposals

    sub.append("reorganize.proposed", "capabilities",
               {"n": len(proposals), "dry_run": not apply})

    if apply and proposals:
        rep.applied = apply_proposals(proposals, sub)
        sub.append("reorganize.applied", "capabilities",
                   {"n": len(rep.applied)})
    else:
        sub.append("reorganize.applied", "capabilities",
                   {"n": 0, "dry_run": True})

    return rep


# ── capability ──────────────────────────────────────────────────────
def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("reorganize")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        rep = run(apply=bool(kwargs.get("apply", False)))
        return rep.to_dict()


_self_register()


__all__ = [
    "DispatchStat",
    "Proposal",
    "Report",
    "apply_proposals",
    "propose",
    "run",
]
