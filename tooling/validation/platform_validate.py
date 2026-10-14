#!/usr/bin/env python3
"""platform_validate.py — validate platform/ on macOS (parse + lint only)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parent.parent


ROOT = _repo_root()
PLATFORM = ROOT / "platform"
errors: list[str] = []

if not PLATFORM.is_dir():
    print(f"platform_validate: platform/ not present at {PLATFORM} — nothing to validate")
    sys.exit(0)

for t in ("yamllint", "shellcheck"):
    if not shutil.which(t):
        print(f"missing tool: {t}  (brew install {t})", file=sys.stderr)
        sys.exit(2)

for p in sorted(PLATFORM.rglob("*.json")):
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        errors.append(f"{p.relative_to(ROOT)}: invalid JSON: {e}")
        continue
    if "declared_only" in d and d["declared_only"] is not True:
        errors.append(f"{p.relative_to(ROOT)}: declared_only must be true")

yaml_files = sorted(list(PLATFORM.rglob("*.yml")) + list(PLATFORM.rglob("*.yaml")))
yamllint_cfg = PLATFORM / ".yamllint"
for y in yaml_files:
    cmd = ["yamllint", "-f", "parsable"]
    if yamllint_cfg.exists():
        cmd += ["-c", str(yamllint_cfg)]
    cmd.append(str(y))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        errors.append(f"{y.relative_to(ROOT)}: yamllint:\n{r.stdout}{r.stderr}")

shell_files = sorted(PLATFORM.rglob("*.sh"))
for s in shell_files:
    r = subprocess.run(["shellcheck", "-f", "gcc", str(s)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        errors.append(f"{s.relative_to(ROOT)}: shellcheck:\n{r.stdout}{r.stderr}")

if errors:
    print("platform_validate: FAIL")
    for e in errors:
        print(" ", e)
    sys.exit(1)

print(f"platform_validate: OK — {len(yaml_files)} YAML, "
      f"{len(list(PLATFORM.rglob('*.json')))} JSON, "
      f"{len(shell_files)} shell all valid")
