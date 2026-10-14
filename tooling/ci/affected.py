#!/usr/bin/env python3
"""affected.py — compute affected components from changed file paths.

Reads component.json dependency edges, inverts them, and returns the set
of components whose own files changed plus every reverse dependency.
Writes the result to affected.json and prints it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "components"


def load_component_json() -> dict[str, dict]:
    out = {}
    for cj in COMPONENTS.rglob("component.json"):
        try:
            doc = json.loads(cj.read_text())
        except Exception:
            continue
        cid = doc.get("component_id")
        if cid:
            out[cid] = {"path": cj.parent, "doc": doc}
    return out


def component_of(path: str, components: dict[str, dict]) -> str | None:
    p = (ROOT / path).resolve()
    for cid, meta in components.items():
        try:
            p.relative_to(meta["path"].resolve())
            return cid
        except ValueError:
            continue
    return None


def changed_files(base_ref: str) -> list[str]:
    r = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    return [l for l in r.stdout.splitlines() if l.strip()]


def reverse_index(components: dict[str, dict]) -> dict[str, set[str]]:
    rev: dict[str, set[str]] = defaultdict(set)
    for cid, meta in components.items():
        deps = meta["doc"].get("dependencies", {}) or {}
        for bucket in deps.values():
            for d in bucket:
                rev[d].add(cid)
    return rev


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    components = load_component_json()
    rev = reverse_index(components)

    direct: set[str] = set()
    for f in changed_files(base_ref):
        cid = component_of(f, components)
        if cid:
            direct.add(cid)

    affected = set(direct)
    q = deque(direct)
    while q:
        cur = q.popleft()
        for dependent in rev.get(cur, set()):
            if dependent not in affected:
                affected.add(dependent)
                q.append(dependent)

    out = {
        "base_ref": base_ref,
        "direct": sorted(direct),
        "affected": sorted(affected),
    }
    (ROOT / "affected.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
