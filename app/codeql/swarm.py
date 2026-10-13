"""CodeQL-style swarm over the fabric's DB.

A query is a named predicate over the joined views:
    capabilities JOIN events JOIN impls

The swarm runs queries in parallel (thread pool), each query
returns rows of findings. No global lock — read-only.

Built-in queries:
    Q1  ghost_real      real rows with no registered impl
    Q2  orphan_home     real rows whose home file does not exist
    Q3  no_dispatch     real rows that were never dispatched
    Q4  stale_asp       aspirational rows with a registered impl
    Q5  genmod_gap      every generated fn code and its _IMPL state
    Q6  dup_home        N real rows sharing one home file (fanout)
    Q7  chain_gap       gaps in events.seq
    Q8  dead_home       home path that no longer exists on disk
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


@dataclass
class Finding:
    q: str
    code: str = ""
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)


# ── helpers ─────────────────────────────────────────────────────
def _con() -> sqlite3.Connection:
    con = sqlite3.connect(DB, timeout=10.0)
    con.execute("PRAGMA busy_timeout=10000")
    return con


def _impl_present(code: str) -> bool:
    try:
        from app.core import capabilities as c
        c._autoload(code)
        return code in c._IMPL
    except Exception:
        return False


# ── Q1: real rows with no registered impl ────────────────────────
def q1_ghost_real() -> list[Finding]:
    con = _con()
    rows = [r[0] for r in con.execute(
        "SELECT code FROM capabilities WHERE status='real' ORDER BY code")]
    con.close()
    out: list[Finding] = []
    for code in rows:
        if not _impl_present(code):
            out.append(Finding(q="ghost_real", code=code))
    return out


# ── Q2: real rows whose home file does not exist ─────────────────
def q2_orphan_home() -> list[Finding]:
    con = _con()
    rows = list(con.execute(
        "SELECT code, home FROM capabilities WHERE status='real' "
        "AND home!='' ORDER BY code"))
    con.close()
    out: list[Finding] = []
    for code, home in rows:
        p = ROOT / home
        if not p.exists():
            out.append(Finding(q="orphan_home", code=code,
                               detail=home,
                               data={"home": home}))
    return out


# ── Q3: real rows never dispatched in ledger ─────────────────────
def q3_no_dispatch() -> list[Finding]:
    con = _con()
    real = [r[0] for r in con.execute(
        "SELECT code FROM capabilities WHERE status='real' ORDER BY code")]
    dispatched: set = set()
    for (payload,) in con.execute(
        "SELECT payload FROM events WHERE kind='dispatch'"):
        try:
            d = json.loads(payload)
            c = d.get("code")
            if c:
                dispatched.add(c)
        except Exception:
            continue
    con.close()
    return [Finding(q="no_dispatch", code=c) for c in real if c not in dispatched]


# ── Q4: aspirational rows with a registered impl ─────────────────
def q4_stale_asp() -> list[Finding]:
    con = _con()
    asp = [r[0] for r in con.execute(
        "SELECT code FROM capabilities WHERE status='aspirational' ORDER BY code")]
    con.close()
    return [Finding(q="stale_asp", code=c) for c in asp if _impl_present(c)]


# ── Q5: every generated fn code and its _IMPL state ──────────────
def q5_genmod_gap() -> list[Finding]:
    con = _con()
    rows = list(con.execute(
        "SELECT code, home FROM capabilities "
        "WHERE home LIKE 'app/generated/%' OR code LIKE 'genmod_%' "
        "ORDER BY code"))
    con.close()
    out: list[Finding] = []
    for code, home in rows:
        ok = _impl_present(code)
        if not ok:
            out.append(Finding(q="genmod_gap", code=code, detail=home,
                               data={"home": home}))
    return out


# ── Q6: N real rows sharing one home file ────────────────────────
def q6_dup_home() -> list[Finding]:
    con = _con()
    rows = list(con.execute(
        "SELECT home, COUNT(*), GROUP_CONCAT(code) FROM capabilities "
        "WHERE status='real' AND home!='' GROUP BY home HAVING COUNT(*)>1 "
        "ORDER BY COUNT(*) DESC LIMIT 40"))
    con.close()
    # only flag generated homes: sharing app/core/nature.py across
    # 23 phenomena is by design; sharing one generated module across
    # many codes means two emitters wrote the same file.
    out = []
    for home, n, codes in rows:
        if not home.startswith("app/generated/"):
            continue
        out.append(Finding(q="dup_home", code=codes.split(",")[0],
                           detail=f"{n} rows share {home}",
                           data={"home": home, "n": n,
                                 "codes": codes.split(",")[:8]}))
    return out


# ── Q7: gaps in events.seq ───────────────────────────────────────
def q7_chain_gap() -> list[Finding]:
    con = _con()
    seqs = [r[0] for r in con.execute("SELECT seq FROM events ORDER BY seq")]
    con.close()
    out: list[Finding] = []
    expected = 1
    for s in seqs:
        if s != expected:
            out.append(Finding(q="chain_gap", code=f"seq:{s}",
                               detail=f"missing {expected}..{s-1}"))
            expected = s
        expected += 1
    return out


# ── Q8: home path referenced but missing on disk ─────────────────
def q8_dead_home() -> list[Finding]:
    con = _con()
    rows = list(con.execute(
        "SELECT DISTINCT home FROM capabilities WHERE home!='' ORDER BY home"))
    con.close()
    out: list[Finding] = []
    for (home,) in rows:
        p = ROOT / home
        if not p.exists():
            out.append(Finding(q="dead_home", code=home, detail=str(p)))
    return out


QUERIES: dict[str, Callable[[], list[Finding]]] = {
    "Q1_ghost_real":  q1_ghost_real,
    "Q2_orphan_home": q2_orphan_home,
    "Q3_no_dispatch": q3_no_dispatch,
    "Q4_stale_asp":   q4_stale_asp,
    "Q5_genmod_gap":  q5_genmod_gap,
    "Q6_dup_home":    q6_dup_home,
    "Q7_chain_gap":   q7_chain_gap,
    "Q8_dead_home":   q8_dead_home,
}


def run_all(*, workers: int = 8) -> dict[str, list[Finding]]:
    results: dict[str, list[Finding]] = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fut = {ex.submit(fn): name for name, fn in QUERIES.items()}
        for f in as_completed(fut):
            name = fut[f]
            try:
                results[name] = f.result()
            except Exception as e:
                results[name] = [Finding(q=name, detail=f"error: {e}")]
    return {k: results[k] for k in QUERIES}


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("swarm")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        which = kwargs.get("which")
        if which:
            fn = QUERIES.get(which)
            if fn is None:
                return {"ok": False, "reason": f"unknown query {which!r}"}
            return {"ok": True, "query": which,
                    "findings": [asdict(f) for f in fn()]}
        r = run_all()
        return {"ok": True,
                "queries": len(r),
                "findings": {k: len(v) for k, v in r.items()}}


_self_register()

__all__ = ["QUERIES", "Finding", "run_all"]
