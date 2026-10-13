#!/usr/bin/env python3
"""Index generated modules into the capability table.

home is the actual .py file path, not the dotted module name.
Only names DEFINED in the module (fn.__module__ == mod_name) are indexed,
so `from typing import Any` does not leak in as a callable.
"""
import importlib
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.capabilities import DB

GEN = ROOT / "app" / "generated"
codes = []
for p in sorted(GEN.glob("*.py")):
    if p.stem == "__init__":
        continue
    mod_name = f"app.generated.{p.stem}"
    try:
        m = importlib.import_module(mod_name)
    except Exception:
        continue
    home = str(p.relative_to(ROOT))          # real file path
    for name, obj in list(vars(m).items()):
        if name.startswith("_"):
            continue
        if not callable(obj):
            continue
        # only functions/classes DEFINED in this module
        if getattr(obj, "__module__", "") != mod_name:
            continue
        codes.append((f"genmod_{p.stem}_{name}", home))

con = sqlite3.connect(DB, timeout=10.0)
con.execute("PRAGMA busy_timeout=10000")

# clean prior broken rows: home is dotted, not a path
con.execute("DELETE FROM capabilities WHERE home LIKE 'app.generated.%' "
            "AND home NOT LIKE 'app/generated/%'")

inserted = 0
for code, home in codes:
    cur = con.execute(
        "INSERT OR IGNORE INTO capabilities "
        "(code,name,category,equation,status,provider,home) "
        "VALUES (?,?,?,?,?,?,?)",
        (code, code, "generated", "synthesized module fn",
         "real", "self", home))
    inserted += cur.rowcount
    if cur.rowcount == 0:
        con.execute("UPDATE capabilities SET home=? WHERE code=?", (home, code))
con.commit()
total = con.execute("SELECT COUNT(*) FROM capabilities").fetchone()[0]
real = con.execute("SELECT COUNT(*) FROM capabilities WHERE status='real'").fetchone()[0]
con.close()
print(f"  indexed {len(codes)} fns ({inserted} new rows; table={total} real={real})")
