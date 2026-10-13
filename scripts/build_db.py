#!/usr/bin/env python3
"""Build the full schema. Real SQLite file. Survives restart."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.core.schema import GAPS, TABLE_NAMES, ddl

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "fabric.sqlite3"
ONT = ROOT / "data" / "ontology.txt"

import sqlite3


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build() -> dict:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(ddl())

    # seed the gap rows themselves — every row is tracked in its own table
    for slug, section, ordinal, desc in GAPS:
        code = f"{section}.{ordinal:02d}.{slug}"
        h = sha(code + "|" + desc)
        con.execute(
            f"INSERT OR IGNORE INTO {slug} "
            f"(code, label, status, source, meta, hash) "
            f"VALUES (?,?,?,?,?,?)",
            (code, desc, "open", f"gap-register:{section}.{ordinal}",
             json.dumps({"section": section, "ordinal": ordinal}), h),
        )

    # seed ontology
    if ONT.exists():
        for i, raw in enumerate(ONT.read_text(encoding="utf-8").splitlines()):
            line = raw.strip()
            if not line or not line.startswith("["):
                continue
            dom, name = line[1:].split("]", 1)
            dom, name = dom.strip(), name.strip()
            code = f"{dom}::{name}"
            con.execute(
                "INSERT OR IGNORE INTO ontology "
                "(domain, name, code, index_in_domain, index_global) "
                "VALUES (?,?,?,?,?)",
                (dom, name, code, i, i),
            )

    # seed registry entries (mirror of ontology + the registry itself)
    con.execute(
        "INSERT OR IGNORE INTO registry_entries "
        "(domain, name, key, path, ordinal, first_class) "
        "VALUES (?,?,?,?,?,?)",
        ("Ontological", "Registry", "Ontological::Registry",
         json.dumps(["Ontological", "Registry"]), 0, 1),
    )
    for r in con.execute("SELECT domain, name, code, index_global FROM ontology"):
        con.execute(
            "INSERT OR IGNORE INTO registry_entries "
            "(domain, name, key, path, ordinal, first_class) "
            "VALUES (?,?,?,?,?,?)",
            (r[0], r[1], r[2], json.dumps([r[0], r[1]]), r[3], 0),
        )

    con.commit()

    # counts
    counts = {}
    for t in TABLE_NAMES:
        counts[t] = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]

    con.close()
    return counts


def verify() -> dict:
    con = sqlite3.connect(DB)
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )]
    total_rows = 0
    for t in tables:
        total_rows += con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    con.close()
    return {"tables": len(tables), "rows": total_rows, "integrity": integrity}


if __name__ == "__main__":
    counts = build()
    print("── build ──")
    print(f"  db          {DB}")
    print(f"  tables      {len(counts)}")
    print(f"  rows total  {sum(counts.values())}")
    print("  selected:")
    for k in ("ontology", "registry_entries",
              "runtime_solver_binaries", "data_evidence_graph",
              "gov_named_authorities", "reg_gdpr", "x_mesh_sec_bridge"):
        if k in counts:
            print(f"    {k:<28} {counts[k]}")

    v1 = verify()
    print()
    print("── verify (first connection closed) ──")
    print(f"  tables      {v1['tables']}")
    print(f"  rows        {v1['rows']}")
    print(f"  integrity   {v1['integrity']}")

    # restart test: open a second connection, confirm counts match
    v2 = verify()
    assert v1 == v2, f"non-deterministic: {v1} != {v2}"
    print()
    print("── restart test ──")
    print("  second open matches first  ✓")
