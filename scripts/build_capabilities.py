#!/usr/bin/env python3
"""Seed the capability registry, wire the bridges, report status."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import sqlite3

from app.core.capabilities import BRIDGES, CAPS, DDL, by_category, status

DB = Path(__file__).resolve().parent.parent / "data" / "fabric.sqlite3"


def main() -> int:
    if not DB.exists():
        print(f"  ! {DB} missing — run scripts/build_db.py first")
        return 2
    con = sqlite3.connect(DB)
    con.executescript(DDL)

    for code, name, cat, eq, st, prov, home in CAPS:
        con.execute(
            "INSERT OR IGNORE INTO capabilities "
            "(code,name,category,equation,status,provider,home) "
            "VALUES (?,?,?,?,?,?,?)",
            (code, name, cat, eq, st, prov, home),
        )
    con.commit()

    inserted = 0
    for cap, gap, gid, kind, note in BRIDGES:
        try:
            con.execute(
                "INSERT OR IGNORE INTO bridges "
                "(src_kind,src_code,dst_kind,dst_code,kind,note) "
                "VALUES ('capability',?,'gap',?,?,?)",
                (cap, f"{gap}#{gid}", kind, note),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass
    con.commit()

    print("── capability registry ──")
    for st, n in sorted(status().items()):
        print(f"  {st:<14} {n}")
    print()
    print("── by category ──")
    for cat, n in by_category().items():
        print(f"  {cat:<12} {n}")
    print()
    n_bridges = con.execute("SELECT COUNT(*) FROM bridges").fetchone()[0]
    print(f"  bridges        {n_bridges}  ({inserted} new)")
    n_caps = con.execute("SELECT COUNT(*) FROM capabilities").fetchone()[0]
    print(f"  total caps     {n_caps}")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
