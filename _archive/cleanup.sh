#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"

echo "== [1/9] fixing sovereign_universal_validator.py =="
if [ -f sovereign_universal_validator.py ]; then
  FIRST=$(head -1 sovereign_universal_validator.py)
  case "$FIRST" in
    "cat "*|"#"*"EOF"*)
      mv sovereign_universal_validator.py sovereign_universal_validator.sh
      echo "  renamed to .sh (shell script, not Python)"
      ;;
    "#!/usr/bin/env python3"*|"#!/usr/bin/python"*)
      awk '/^EOF$/{exit} {print}' sovereign_universal_validator.py > /tmp/suv.py && \
        mv /tmp/suv.py sovereign_universal_validator.py
      echo "  truncated at EOF marker"
      ;;
    *)
      echo "  unrecognized header, leaving alone"
      ;;
  esac
fi

echo "== [2/9] removing local env directories =="
rm -rf .venv312 .lanes .venv
echo "  done"

echo "== [3/9] updating .gitignore =="
for entry in \
  ".venv/" ".venv312/" ".lanes/" \
  "constructors/" "sovereign-bounded-matrix/" \
  ".spec-fix-backups/" "docs/site_output/" "logs/" \
  "*.bak" "*.bak.*" "*.mmap" "*.db" "*.log" \
  "uvicorn.log" "botnet.db" "state.mmap" "affected.json" \
  "__pycache__/" "*.egg-info/" "build/" "dist/" ".pytest_cache/"
do
  grep -qxF "$entry" .gitignore 2>/dev/null || echo "$entry" >> .gitignore
done
echo "  rules appended"

echo "== [4/9] untracking build artifacts =="
for d in constructors sovereign-bounded-matrix .spec-fix-backups docs/site_output logs .venv312 .lanes .venv; do
  [ -d "$d" ] && git rm -r --cached "$d" > /dev/null 2>&1 && echo "  untracked $d" || true
done
find . -type f \( -name '*.bak' -o -name '*.bak.*' -o -name '*.mmap' -o -name '*.log' -o -name 'uvicorn.log' -o -name 'state.mmap' -o -name 'affected.json' \) \
  -not -path './.git/*' -not -path './.venv312/*' -not -path './.lanes/*' -not -path './.venv/*' \
  -exec git rm --cached {} \; > /dev/null 2>&1
echo "  untracked loose artifacts"

echo "== [5/9] writing ruff policy =="
python3 - <<'PY'
from pathlib import Path
p = Path("pyproject.toml")
if p.exists():
    src = p.read_text()
else:
    src = ""
block = '''
[tool.ruff]
line-length = 100
exclude = [
    ".venv", ".venv312", ".lanes",
    "constructors", "sovereign-bounded-matrix",
    ".spec-fix-backups", "docs/site_output", "logs",
]

[tool.ruff.lint]
ignore = [
    "E402",
    "E731",
    "E741",
    "F403",
    "F405",
    "F841",
]
'''
if "[tool.ruff]" not in src:
    src = src.rstrip() + "\n" + block
    p.write_text(src)
    print("  pyproject.toml updated")
else:
    print("  [tool.ruff] already present, not touching")
PY

echo "== [6/9] running ruff autofix on tracked files only =="
git ls-files '*.py' | xargs -r python3 -m ruff check --fix --line-length=100 2>/dev/null | tail -3 || true
git ls-files '*.py' | xargs -r python3 -m ruff format --line-length=100 2>/dev/null | tail -3 || true

echo "== [7/9] checking what still fails to parse =="
FAILS=$(git ls-files '*.py' | while read -r f; do
  [ -f "$f" ] || continue
  python3 -m py_compile "$f" 2>/dev/null || echo "$f"
done)
if [ -z "$FAILS" ]; then
  echo "  every tracked .py parses"
else
  echo "  syntax errors in:"
  echo "$FAILS" | head -40
fi

echo "== [8/9] re-enabling pre-commit and running hooks =="
git config --unset core.hooksPath 2>/dev/null || true
python3 -m pre_commit run --all-files 2>&1 | tail -30 || true

echo "== [9/9] summary =="
echo "  git status:"
git status --short | head -20
echo "  staged files: $(git diff --cached --name-only | wc -l | tr -d ' ')"
echo "  unstaged modified: $(git diff --name-only | wc -l | tr -d ' ')"
echo
echo "done. review, then:"
echo "  git add -A"
echo "  git commit -m 'chore: whitespace policy, import fixes, untrack build artifacts'"
echo "  git push origin main"
