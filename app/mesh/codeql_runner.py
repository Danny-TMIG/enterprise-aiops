from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _codeql_bin() -> str | None:
    p = shutil.which("codeql")
    if p:
        return p
    for cand in (Path.home() / ".codeql" / "codeql",
                 Path.home() / ".codeql" / "codeql-bin" / "codeql",
                 Path("/usr/local/bin/codeql"),
                 Path("/opt/homebrew/bin/codeql"),
                 Path("/usr/local/share/codeql/codeql")):
        if cand.exists() and os.access(str(cand), os.X_OK):
            return str(cand)
    return None


def run_codeql(project_root: str, work_dir: str | None = None,
               timeout: int = 1800) -> str | None:
    codeql = _codeql_bin()
    if not codeql:
        return None
    root = Path(project_root).resolve()
    work = Path(work_dir or root)
    db_dir = work / ".mesh-codeql-db"
    sarif = work / ".mesh-codeql.sarif"
    pack_dir = root / "codeql" / "packs" / "mesh-queries"
    try:
        r = subprocess.run(
            [codeql, "database", "create", str(db_dir),
             "--language=python", f"--source-root={root}", "--overwrite"],
            capture_output=True, text=True, timeout=timeout,
        )
        if r.returncode != 0:
            return None
        if pack_dir.exists():
            cmd = [codeql, "database", "analyze", str(db_dir), str(pack_dir),
                   "--format=sarif-latest", f"--output={sarif}", "--download"]
        else:
            cmd = [codeql, "database", "analyze", str(db_dir),
                   "--format=sarif-latest", f"--output={sarif}", "--download",
                   "codeql/python-queries:codeql-suites/python-security-extended.qls"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return str(sarif) if sarif.exists() else None
    except Exception:
        return None
