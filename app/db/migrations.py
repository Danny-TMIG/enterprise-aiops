"""Run fabric migrations.

The schema is built idempotently by scripts/build_db.py. This module
exposes the same operation as a callable so init_db.py and other
bootstrap paths can run it without shelling out.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


def run_migrations(path: Path | None = None) -> dict[str, Any]:
    """Apply the base schema. Idempotent. Returns a report dict."""
    p = Path(path) if path else DB
    p.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {"path": str(p), "applied": 0, "skipped": 0}
    try:
        from app.core.schema import ddl
    except Exception as e:
        report["error"] = f"schema import failed: {e}"
        return report
    con = sqlite3.connect(p)
    before = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    con.executescript(ddl())
    after = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    con.commit()
    con.close()
    report["applied"] = len(after - before)
    report["skipped"] = len(after & before)
    report["tables"] = len(after)
    return report


__all__ = ["DB", "run_migrations"]
