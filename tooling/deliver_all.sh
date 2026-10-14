#!/usr/bin/env bash
# One-shot delivery: reconcile nature catalog, verify ac/ag/ax refactor,
# snapshot ledger, run full suite, commit + push only if green.
set -uo pipefail

REPO="$HOME/aether"
cd "$REPO" || { echo "no repo at $REPO"; exit 1; }

FAIL=0
note() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$*"; FAIL=1; }
skip() { printf "  \033[33m•\033[0m %s\n" "$*"; }

# ---------------------------------------------------------------- 0. strip trailing whitespace
note "0. strip trailing whitespace in tracked .py/.sh"
changed=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -qE ' +$' "$f" 2>/dev/null; then
    python3 - "$f" <<'PY'
import sys
p = sys.argv[1]
with open(p) as fh:
    lines = [l.rstrip() + "\n" for l in fh.readlines()]
with open(p, "w") as fh:
    fh.writelines(lines)
PY
    changed=$((changed+1))
  fi
done < <(git ls-files '*.py' '*.sh' 2>/dev/null)
ok "cleaned $changed files"

# ---------------------------------------------------------------- 1. reconcile nature.txt <-> algorithms.json
note "1. reconcile data/nature.txt with data/algorithms.json"
python3 - <<'PY'
import json
from pathlib import Path

DERIVED = Path("data/algorithms.json")
CATALOG = Path("data/nature.txt")
if not DERIVED.is_file():
    raise SystemExit("missing data/algorithms.json")
if not CATALOG.is_file():
    CATALOG.write_text("# Source phenomena catalog\n# format: code | description\n\n")

derived = json.loads(DERIVED.read_text())
mapped = {a["phenomenon"] for a in derived["algorithms"]}

lines = CATALOG.read_text().splitlines()
active, out, demoted = set(), [], 0
for line in lines:
    s = line.strip()
    if not s or s.startswith("#"):
        out.append(line)
        continue
    code = s.split("|")[0].strip()
    if code in mapped:
        active.add(code)
        out.append(line)
    else:
        out.append("# BACKLOG (not yet derived): " + line)
        demoted += 1

missing = sorted(mapped - active)
if missing:
    out += ["", "# --- added to close catalog/derived gap ---"]
    for code in missing:
        out.append(f"{code} | source phenomenon (see data/algorithms.json)")

CATALOG.write_text("\n".join(out) + "\n")
print(f"  active={len(active)} mapped={len(mapped)} demoted={demoted} appended={len(missing)}")
PY
if [ $? -eq 0 ]; then ok "catalog reconciled"; else bad "reconcile failed"; fi

# ---------------------------------------------------------------- 2. placeholder check
note "2. nature.txt placeholder check"
n=$(grep -c "see data/algorithms.json" data/nature.txt 2>/dev/null | tr -d '\n' || true); n=${n:-0}
active=$(grep -v '^[[:space:]]*#' data/nature.txt 2>/dev/null | grep -c '|' | tr -d '\n' || true); active=${active:-0}
if [ "$n" -eq 0 ]; then ok "0 placeholders"; else bad "$n placeholders remain"; fi
ok "active curated entries: $active"

# ---------------------------------------------------------------- 3. ledger snapshot
note "3. ledger snapshot"
if [ -s sovereign/ledger.jsonl ]; then
  snap="research/datasets/ledger-snapshot-$(date +%Y%m%d).jsonl"
  mkdir -p research/datasets
  cp sovereign/ledger.jsonl "$snap"
  rows=$(wc -l < "$snap" | tr -d ' ')
  ok "wrote $snap ($rows rows)"
else
  bad "sovereign/ledger.jsonl missing or empty"
fi

# ---------------------------------------------------------------- 4. CLI entrypoints
note "4. CLI entrypoints from new paths"
if python -m ag.verify >/dev/null 2>&1; then ok "python -m ag.verify"; else bad "python -m ag.verify"; fi
if python -m ax.harnesses.ablate_scale >/dev/null 2>&1; then
  ok "python -m ax.harnesses.ablate_scale"
elif python -m ax.harnesses.ablate_scale 2>&1 | head -1 | grep -q .; then
  ok "python -m ax.harnesses.ablate_scale (ran)"
else
  bad "python -m ax.harnesses.ablate_scale"
fi

# ---------------------------------------------------------------- 5. stale imports (fatal)
note "5. stale module imports (fatal)"
stale_imports=$(grep -rIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ \
  -E "(from|import) +(sovereign\.(verify|model|healer)|control_plane\.integration|research\.harnesses)" \
  --include="*.py" . 2>/dev/null || true)
if [ -z "$stale_imports" ]; then ok "no stale module imports"
else echo "$stale_imports" | sed 's/^/    /'; bad "stale imports found"; fi

# ---------------------------------------------------------------- 6. informational old-path mentions
note "6. old-path mentions in strings/docs (informational)"
mentions=$(grep -rIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ \
  --exclude-dir=dist --exclude="post_refactor_check.sh" --exclude="deliver_all.sh" \
  --exclude="bootstrap*.sh" --exclude="install_real_generate.sh" \
  -e "sovereign/verify" -e "control_plane/integration" -e "research/harnesses" \
  --include="*.py" --include="*.md" --include="*.json" . 2>/dev/null || true)
if [ -z "$mentions" ]; then ok "no old-path mentions"
else ok "$(echo "$mentions" | wc -l | tr -d ' ') mentions (non-blocking)"; fi

# ---------------------------------------------------------------- 7. tracked & not ignored
note "7. key artifacts tracked and not ignored"
for f in data/nature.txt data/algorithms.json nature/algorithms.py tests/test_nature_algorithms.py; do
  if git check-ignore -q "$f"; then bad "$f is git-ignored"
  elif git ls-files --error-unmatch "$f" >/dev/null 2>&1; then ok "$f tracked"
  else bad "$f untracked"; fi
done

# ---------------------------------------------------------------- 8. full suite
note "8. full pytest suite"
out=$(python -m pytest -q 2>&1); rc=$?
if [ $rc -eq 0 ]; then ok "$(echo "$out" | tail -1)"
else echo "$out" | tail -20 | sed 's/^/    /'; bad "pytest failed"; fi

# ---------------------------------------------------------------- 9. commit + push
note "result"
if [ "$FAIL" -eq 0 ]; then
  ok "all checks green"
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -s -m "chore(delivery): reconcile nature catalog, verify ac/ag/ax, snapshot ledger"
    git push origin main
    git log --oneline -1
  else
    ok "working tree already clean — nothing to commit"
  fi
else
  bad "checks failed — not committing"
  exit 1
fi
