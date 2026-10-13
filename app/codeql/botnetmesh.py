"""CodeQL · SQL · MQL botnet mesh.

One schema, three query languages, one swarm.

Schema (SQLite):
    bots     (id, hostname, os, arch, registered_at, last_seen, status)
    tasks    (id, bot_id, cmd, args, queued_at, dispatched_at,
              completed_at, status)
    results  (id, task_id, bot_id, payload, success, received_at)
    events   (id, kind, subject, payload, ts)

Query languages:
    SQL   — SELECT ... FROM ... WHERE ...
    MQL   — mongo-style {"field": {"$op": value}} filters, compiled to SQL
    CQL   — codeql-style: named query, scope, predicate, findings

The mesh runs every query in parallel; findings are normalized to
(q, table, row_id, detail). No global lock — read-only.
"""
from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


# ── schema ──────────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS bots (
    id            TEXT PRIMARY KEY,
    hostname      TEXT,
    os            TEXT,
    arch          TEXT,
    registered_at REAL,
    last_seen     REAL,
    status        TEXT NOT NULL DEFAULT 'active'
);
CREATE INDEX IF NOT EXISTS ix_bots_status ON bots(status);
CREATE INDEX IF NOT EXISTS ix_bots_lastseen ON bots(last_seen);

CREATE TABLE IF NOT EXISTS tasks (
    id            TEXT PRIMARY KEY,
    bot_id        TEXT NOT NULL,
    cmd           TEXT NOT NULL,
    args          TEXT DEFAULT '{}',
    queued_at     REAL,
    dispatched_at REAL,
    completed_at  REAL,
    status        TEXT NOT NULL DEFAULT 'queued'
);
CREATE INDEX IF NOT EXISTS ix_tasks_bot ON tasks(bot_id);
CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks(status);

CREATE TABLE IF NOT EXISTS results (
    id            TEXT PRIMARY KEY,
    task_id       TEXT NOT NULL,
    bot_id        TEXT NOT NULL,
    payload       TEXT,
    success       INTEGER NOT NULL DEFAULT 0,
    received_at   REAL
);
CREATE INDEX IF NOT EXISTS ix_results_bot ON results(bot_id);
CREATE INDEX IF NOT EXISTS ix_results_task ON results(task_id);
"""


def ensure_schema() -> sqlite3.Connection:
    con = sqlite3.connect(DB, timeout=10.0)
    con.execute("PRAGMA busy_timeout=10000")
    con.executescript(DDL)
    con.commit()
    return con


def seed_demo(n_bots: int = 24) -> dict[str, int]:
    """Seed the botnetmesh tables. Idempotent per-id."""
    con = ensure_schema()
    now = time.time()
    for i in range(n_bots):
        bid = f"bot-{i:03d}"
        con.execute(
            "INSERT OR IGNORE INTO bots "
            "(id,hostname,os,arch,registered_at,last_seen,status) "
            "VALUES (?,?,?,?,?,?,?)",
            (bid, f"h{i+1}", ["linux","windows","darwin"][i % 3],
             ["x86_64","arm64"][i % 2], now - 3600, now - 60*(i % 20),
             "active" if i % 5 else "terminated"))
        for j in range(3):
            tid = f"task-{i:03d}-{j}"
            con.execute(
                "INSERT OR IGNORE INTO tasks "
                "(id,bot_id,cmd,args,queued_at,dispatched_at,status) "
                "VALUES (?,?,?,?,?,?,?)",
                (tid, bid, ["ping","inventory","heartbeat"][j],
                 json.dumps({"n": j}), now - 300, now - 200,
                 ["queued","sent","completed"][j]))
            if j == 2:
                con.execute(
                    "INSERT OR IGNORE INTO results "
                    "(id,task_id,bot_id,payload,success,received_at) "
                    "VALUES (?,?,?,?,?,?)",
                    (f"res-{i:03d}-{j}", tid, bid,
                     json.dumps({"ok": True, "n": j}), 1, now - 100))
    con.commit()
    counts = {}
    for t in ("bots","tasks","results"):
        counts[t] = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    con.close()
    return counts


# ── MQL → SQL compiler ──────────────────────────────────────────
MQL_OPS = {
    "$eq": "=", "$ne": "!=", "$gt": ">", "$gte": ">=",
    "$lt": "<", "$lte": "<=", "$like": "LIKE", "$not_like": "NOT LIKE",
    "$in": "IN", "$nin": "NOT IN",
}


def compile_mql(table: str, filt: dict[str, Any],
                projection: list[str] | None = None,
                limit: int | None = None) -> tuple[str, list[Any]]:
    """Mongo-style filter -> SQL. Values are bound, not interpolated."""
    cols = ", ".join(projection) if projection else "*"
    where: list[str] = []
    params: list[Any] = []
    for key, val in (filt or {}).items():
        if isinstance(val, dict):
            for op, arg in val.items():
                sql_op = MQL_OPS.get(op)
                if sql_op is None:
                    raise ValueError(f"unknown MQL op {op!r}")
                if sql_op in ("IN","NOT IN"):
                    if not arg:
                        where.append("0=1" if sql_op == "IN" else "1=1")
                        continue
                    ph = ",".join("?" * len(arg))
                    where.append(f"{key} {sql_op} ({ph})")
                    params.extend(arg)
                else:
                    where.append(f"{key} {sql_op} ?")
                    params.append(arg)
        else:
            where.append(f"{key} = ?")
            params.append(val)
    sql = f"SELECT {cols} FROM {table}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    if limit:
        sql += f" LIMIT {int(limit)}"
    return sql, params


def run_mql(table: str, filt: dict[str, Any], **kw) -> list[dict[str, Any]]:
    sql, params = compile_mql(table, filt, **kw)
    con = ensure_schema()
    cur = con.execute(sql, params)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    con.close()
    return rows


def run_sql(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
    con = ensure_schema()
    cur = con.execute(sql, tuple(params))
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    con.close()
    return rows


# ── CQL: CodeQL-style named queries ─────────────────────────────
@dataclass
class Finding:
    q: str
    table: str
    row_id: str
    detail: str = ""
    data: dict[str, Any] = field(default_factory=dict)


def q_silent_bots() -> list[Finding]:
    """Bots that haven't checked in for over 300 seconds."""
    rows = run_sql(
        "SELECT id, last_seen FROM bots "
        "WHERE status='active' AND (? - last_seen) > 300", (time.time(),))
    return [Finding(q="silent_bots", table="bots", row_id=r["id"],
                    detail=f"silent {int(time.time()-r['last_seen'])}s")
            for r in rows]


def q_orphan_tasks() -> list[Finding]:
    """Tasks whose bot no longer exists."""
    rows = run_sql(
        "SELECT t.id, t.bot_id FROM tasks t "
        "LEFT JOIN bots b ON b.id = t.bot_id WHERE b.id IS NULL")
    return [Finding(q="orphan_tasks", table="tasks", row_id=r["id"],
                    detail=f"bot {r['bot_id']} missing")
            for r in rows]


def q_queued_long() -> list[Finding]:
    """Tasks stuck in queued for over 600 seconds."""
    rows = run_sql(
        "SELECT id, queued_at FROM tasks "
        "WHERE status='queued' AND (? - queued_at) > 600", (time.time(),))
    return [Finding(q="queued_long", table="tasks", row_id=r["id"],
                    detail=f"queued {int(time.time()-r['queued_at'])}s")
            for r in rows]


def q_failed_tasks() -> list[Finding]:
    """Tasks whose result has success=0."""
    rows = run_sql(
        "SELECT t.id, r.payload FROM tasks t "
        "JOIN results r ON r.task_id = t.id WHERE r.success = 0")
    return [Finding(q="failed_tasks", table="tasks", row_id=r["id"],
                    detail=(r["payload"] or "")[:60])
            for r in rows]


def q_terminated_with_tasks() -> list[Finding]:
    """Terminated bots that still have queued tasks."""
    rows = run_sql(
        "SELECT b.id AS bid, COUNT(t.id) AS n FROM bots b "
        "JOIN tasks t ON t.bot_id = b.id "
        "WHERE b.status='terminated' AND t.status='queued' "
        "GROUP BY b.id")
    return [Finding(q="terminated_with_tasks", table="bots", row_id=r["bid"],
                    detail=f"{r['n']} queued",
                    data={"queued": r["n"]}) for r in rows]


def q_success_ratio() -> list[Finding]:
    """Bots whose result success ratio is below 0.5."""
    rows = run_sql(
        "SELECT bot_id, AVG(success) AS s, COUNT(*) AS n FROM results "
        "GROUP BY bot_id HAVING s < 0.5")
    return [Finding(q="success_ratio", table="results", row_id=r["bot_id"],
                    detail=f"avg {r['s']:.2f} over {r['n']}")
            for r in rows]


# ── mesh: run CQL + SQL + MQL in parallel ────────────────────────
@dataclass
class MeshResult:
    cql: dict[str, list[Finding]] = field(default_factory=dict)
    sql: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    mql: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cql": {k: [asdict(f) for f in v] for k, v in self.cql.items()},
            "sql": self.sql,
            "mql": self.mql,
        }


CQL_QUERIES: dict[str, Callable[[], list[Finding]]] = {
    "silent_bots":           q_silent_bots,
    "orphan_tasks":          q_orphan_tasks,
    "queued_long":           q_queued_long,
    "failed_tasks":          q_failed_tasks,
    "terminated_with_tasks": q_terminated_with_tasks,
    "success_ratio":         q_success_ratio,
}

SQL_QUERIES: dict[str, tuple[str, Sequence[Any]]] = {
    "bot_os_counts": (
        "SELECT os, COUNT(*) n FROM bots GROUP BY os ORDER BY n DESC", ()),
    "task_status": (
        "SELECT status, COUNT(*) n FROM tasks GROUP BY status", ()),
    "oldest_bot": (
        "SELECT id, registered_at FROM bots "
        "ORDER BY registered_at ASC LIMIT 5", ()),
}

MQL_QUERIES: dict[str, tuple[str, dict[str, Any]]] = {
    "active_linux":   ("bots", {"status": "active", "os": "linux"}),
    "recent_bots":    ("bots", {"last_seen": {"$gt": time.time() - 300}}),
    "ping_tasks":     ("tasks", {"cmd": "ping"}),
    "unsuccessful":   ("results", {"success": 0}),
    "multi_cmd":      ("tasks", {"cmd": {"$in": ["ping", "inventory"]}}),
}


def run_mesh(*, workers: int = 8) -> MeshResult:
    res = MeshResult()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for name, fn in CQL_QUERIES.items():
            futs[ex.submit(fn)] = ("cql", name)
        for name, (sql, params) in SQL_QUERIES.items():
            futs[ex.submit(run_sql, sql, params)] = ("sql", name)
        for name, (t, f) in MQL_QUERIES.items():
            futs[ex.submit(run_mql, t, f)] = ("mql", name)
        for f in as_completed(futs):
            kind, name = futs[f]
            try:
                out = f.result()
            except Exception as e:
                out = [] if kind != "cql" else [
                    Finding(q=name, table="?", row_id="?", detail=str(e))]
            if kind == "cql":
                res.cql[name] = out
            elif kind == "sql":
                res.sql[name] = out
            else:
                res.mql[name] = out
    return res


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("botnetmesh")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        ensure_schema()
        seed = seed_demo()
        mesh = run_mesh()
        d = mesh.to_dict()
        summary = {
            "cql": {k: len(v) for k, v in mesh.cql.items()},
            "sql": {k: len(v) for k, v in mesh.sql.items()},
            "mql": {k: len(v) for k, v in mesh.mql.items()},
        }
        return {"schema": seed, "queries": summary, "mesh": d}


_self_register()

__all__ = [
    "CQL_QUERIES",
    "MQL_QUERIES",
    "SQL_QUERIES",
    "Finding",
    "compile_mql",
    "ensure_schema",
    "run_mesh",
    "run_mql",
    "run_sql",
    "seed_demo",
]
