"""Hardened C2 server, SQLite-backed."""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from app.botnetmastery.models import Bot, Task

_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS bots (
    id            TEXT PRIMARY KEY,
    hostname      TEXT NOT NULL DEFAULT '',
    os            TEXT NOT NULL DEFAULT '',
    arch          TEXT NOT NULL DEFAULT '',
    last_seen     REAL NOT NULL,
    status        TEXT NOT NULL DEFAULT 'active',
    registered_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id            TEXT PRIMARY KEY,
    bot_id        TEXT NOT NULL,
    cmd           TEXT NOT NULL,
    args          TEXT NOT NULL DEFAULT '{}',
    status        TEXT NOT NULL DEFAULT 'queued',
    created_at    REAL NOT NULL,
    dispatched_at REAL,
    completed_at  REAL
);
CREATE INDEX IF NOT EXISTS idx_tasks_bot_status ON tasks(bot_id, status);
CREATE TABLE IF NOT EXISTS results (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    TEXT NOT NULL,
    bot_id     TEXT NOT NULL,
    output     TEXT NOT NULL,
    success    INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_results_bot ON results(bot_id);
CREATE TABLE IF NOT EXISTS control (
    key TEXT PRIMARY KEY, value TEXT NOT NULL
);
"""


class _AttrDict(dict):
    """A dict that also exposes keys as attributes."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class C2Server:
    def __init__(self, db_path: str = "botnet.db", *args, **kwargs):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            self.db_path, check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.close()
            except Exception:
                pass

    # ── bots ────────────────────────────────────────────────
    def register_bot(self, bot: Bot) -> str:
        with self._lock:
            now = time.time()
            self._conn.execute(
                "INSERT INTO bots(id, hostname, os, arch, last_seen, "
                " status, registered_at) VALUES(?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET "
                " hostname=excluded.hostname, os=excluded.os, "
                " arch=excluded.arch, last_seen=excluded.last_seen, "
                " status=excluded.status",
                (bot.id, getattr(bot, "hostname", ""),
                 getattr(bot, "os", ""), getattr(bot, "arch", ""),
                 getattr(bot, "last_seen", now) or now,
                 getattr(bot, "status", "active") or "active", now),
            )
        return bot.id

    def get_bot(self, bot_id: str) -> _AttrDict:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM bots WHERE id=?", (bot_id,)).fetchone()
        if row is None:
            raise KeyError(f"bot {bot_id!r} not found")
        d = _AttrDict(dict(row))
        d["bot_id"] = d["id"]
        return d

    def list_bots(self, status: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if status is None:
                rows = self._conn.execute(
                    "SELECT * FROM bots ORDER BY registered_at").fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT * FROM bots WHERE status=? "
                    "ORDER BY registered_at", (status,)).fetchall()
        return [dict(r) for r in rows]

    # ── tasks ───────────────────────────────────────────────
    def queue_task(self, task: Task) -> str:
        if self.kill_switch_engaged():
            raise RuntimeError("kill switch engaged: queue blocked")
        with self._lock:
            self._conn.execute(
                "INSERT INTO tasks(id, bot_id, cmd, args, status, created_at) "
                "VALUES(?,?,?,?,'queued',?)",
                (task.id, task.bot_id, task.cmd,
                 json.dumps(getattr(task, "args", {}) or {}), time.time()),
            )
        return task.id

    def pending_tasks(self,
                      bot_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if bot_id is None:
                rows = self._conn.execute(
                    "SELECT * FROM tasks WHERE status IN "
                    "('queued','sent') ORDER BY created_at").fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT * FROM tasks WHERE bot_id=? "
                    "AND status IN ('queued','sent') ORDER BY created_at",
                    (bot_id,)).fetchall()
        return [dict(r) for r in rows]

    def dispatch(self, bot_id: str) -> dict[str, Any] | None:
        if self.kill_switch_engaged():
            return None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM tasks WHERE bot_id=? AND status='queued' "
                "ORDER BY created_at LIMIT 1", (bot_id,)).fetchone()
            if row is None:
                return None
            now = time.time()
            self._conn.execute(
                "UPDATE tasks SET status='sent', dispatched_at=? WHERE id=?",
                (now, row["id"]))
            self._conn.execute(
                "UPDATE bots SET last_seen=? WHERE id=?", (now, bot_id))
        out = dict(row)
        out["status"] = "sent"
        out["dispatched_at"] = now
        return out

    def complete(self, task_id: str, bot_id: str, output: str,
                 success: bool = True) -> int:
        with self._lock:
            now = time.time()
            cur = self._conn.execute(
                "INSERT INTO results(task_id, bot_id, output, success, "
                " created_at) VALUES(?,?,?,?,?)",
                (task_id, bot_id, output, 1 if success else 0, now))
            self._conn.execute(
                "UPDATE tasks SET status='done', completed_at=? WHERE id=?",
                (now, task_id))
        return cur.lastrowid

    def results_for(self, bot_id: str) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM results WHERE bot_id=? ORDER BY id",
                (bot_id,)).fetchall()
        return [dict(r) for r in rows]

    # ── control ─────────────────────────────────────────────
    def engage_kill_switch(self,
                           reason: str = "manual") -> dict[str, Any]:
        with self._lock:
            now = time.time()
            self._conn.execute(
                "INSERT OR REPLACE INTO control(key, value) "
                "VALUES('kill', ?)",
                (json.dumps({"reason": reason, "at": now}),))
            self._conn.execute(
                "UPDATE bots SET status='terminated' WHERE status='active'")
            self._conn.execute(
                "UPDATE tasks SET status='cancelled' "
                "WHERE status IN ('queued','sent')")
        return {"status": "terminated", "reason": reason, "at": now}

    def kill_switch_engaged(self) -> bool:
        with self._lock:
            row = self._conn.execute(
                "SELECT value FROM control WHERE key='kill'").fetchone()
        return row is not None

    def revoke_all_commands(self) -> int:
        with self._lock:
            cur = self._conn.execute(
                "UPDATE tasks SET status='revoked' "
                "WHERE status IN ('queued','sent')")
        return cur.rowcount or 0

    def heartbeat(self, bot_id: str) -> float:
        with self._lock:
            now = time.time()
            cur = self._conn.execute(
                "UPDATE bots SET last_seen=?, status='active' WHERE id=?",
                (now, bot_id))
            if cur.rowcount == 0:
                raise KeyError(f"bot {bot_id!r} not found")
        return now


class C2Controller:

    """Sandboxed command-and-control controller for the simulation.

    Tracks a set of simulated bots; `poll()` returns their state. The
    controller never opens sockets, never sends commands to real hosts.
    `engage_kill_switch()` marks the controller as inert; further calls
    to `poll()` reflect that.
    """
    def __init__(self, db_path: str = ":memory:", bots=None, seed: int = 0):
        self.db_path = db_path
        self.seed = seed
        self.kill_switch = False
        self.bots: dict = {}
        self.history: list = []
        if bots:
            for b in bots:
                self.add_bot(b)

    def add_bot(self, bot) -> BotModel:
        self.bots[bot.id] = bot
        return bot

    def engage_kill_switch(self) -> None:
        self.kill_switch = True
        for b in self.bots.values():
            b.status = "terminated"

    def tick(self) -> dict:
        """Advance one simulation step and return the observation."""
        import time
        now = time.time()
        for b in self.bots.values():
            b.last_seen = now
        obs = self.poll()
        self.history.append(obs)
        return obs

    def poll(self) -> dict:
        import time
        return {
            "ts": time.time(),
            "count": len(self.bots),
            "kill_switch": self.kill_switch,
            "bots": {bid: b.to_dict() for bid, b in self.bots.items()},
        }

