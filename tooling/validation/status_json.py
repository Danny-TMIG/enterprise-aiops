#!/usr/bin/env python3
"""Emit a static status.json snapshot for the frontend to read.

Wraps tooling/validation/status.py --json and writes the result to
web/public/status.json. Read-only with respect to the repo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parent.parent


def main() -> int:
    root = _repo_root()
    script = root / "tooling" / "validation" / "status.py"
    out = root / "web" / "public" / "status.json"

    r = subprocess.run(
        [sys.executable, str(script), "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode not in (0, 1):
        print(f"status.py failed: exit {r.returncode}", file=sys.stderr)
        print(r.stderr, file=sys.stderr)
        return 2

    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        print(f"status.py produced invalid JSON: {e}", file=sys.stderr)
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True))
    print(f"wrote {out.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
