"""Database health probe.

Returns a dict describing the fabric's database state. Read-only.
Never raises — a down database is a health finding, not an exception.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


def db_health(path: Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else DB
    out: dict[str, Any] = {
        "path": str(p),
        "exists": p.exists(),
    }
    if not p.exists():
        out["ok"] = False
        out["reason"] = "database file missing"
        return out
    try:
        con = sqlite3.connect(p)
        out["integrity"] = con.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        out["tables"] = len(tables)
        out["events"] = 0
        if "events" in tables:
            out["events"] = con.execute(
                "SELECT COUNT(*) FROM events").fetchone()[0]
        con.close()
        out["ok"] = (out["integrity"] == "ok")
    except Exception as e:
        out["ok"] = False
        out["reason"] = f"{type(e).__name__}: {e}"
    return out


__all__ = ["DB", "db_health"]
