#!/usr/bin/env python3
"""platform_validate.py — validate platform/ on macOS (parse + lint only)."""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

from pathlib import Path as _Path
def _find_repo_root(start=None):
    p = (start or _Path(__file__)).resolve()
    if p.is_file(): p = p.parent
    for parent in [p, *p.parents]:
        if (parent / 'pyproject.toml').exists(): return parent
    return p.parent.parent
_REPO_ROOT = _find_repo_root()

ROOT = _REPO_ROOT
PLATFORM = ROOT / "platform"
errors: list[str] = []

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
    for line in r.stdout.splitlines():
        if line.strip():
            errors.append(f"yamllint {y.relative_to(ROOT)}: {line}")

for sh in sorted(PLATFORM.rglob("*.sh")):
    r = subprocess.run(["shellcheck", "-S", "warning", "-f", "gcc", str(sh)], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.strip():
            errors.append(f"shellcheck {sh.relative_to(ROOT)}: {line}")

for ks in sorted(PLATFORM.rglob("*.ks")):
    if "$(" in ks.read_text():
        errors.append(f"{ks.relative_to(ROOT)}: unquoted command substitution in kickstart")

limits = PLATFORM / "LIMITS.md"
if not limits.exists():
    errors.append("platform/LIMITS.md missing")
else:
    text = limits.read_text()
    for sub in sorted(p.name for p in PLATFORM.iterdir() if p.is_dir()):
        if sub not in text:
            errors.append(f"LIMITS.md does not mention platform/{sub}")

for sub in sorted(p for p in PLATFORM.iterdir() if p.is_dir()):
    if not [f for f in sub.rglob("*") if f.is_file()]:
        errors.append(f"platform/{sub.name} is empty")

if errors:
    print(f"platform_validate: {len(errors)} error(s)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"platform_validate: OK — {len(yaml_files)} YAML, "
      f"{len(list(PLATFORM.rglob('*.json')))} JSON, "
      f"{len(list(PLATFORM.rglob('*.sh')))} shell, "
      f"{len(list(PLATFORM.rglob('*.ks')))} kickstart all valid")
sys.exit(0)
