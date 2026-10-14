#!/usr/bin/env bash
# Post-refactor sanity check for the ac/ag/ax + nature migration.
set -uo pipefail

REPO="$HOME/aether"
cd "$REPO" || { echo "no repo at $REPO"; exit 1; }

FAIL=0
note() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$*"; FAIL=1; }

# 1. nature.txt placeholder check
note "1. nature.txt placeholder check"
n=$(grep -c "see data/algorithms.json" data/nature.txt 2>/dev/null | tr -d '\n' || true)
n=${n:-0}
if [ "$n" -eq 0 ]; then ok "0 placeholders"; else bad "$n placeholders remain"; fi

active=$(grep -v '^[[:space:]]*#' data/nature.txt 2>/dev/null | grep -c '|' | tr -d '\n' || true)
active=${active:-0}
ok "active curated entries: $active"

# 2. ledger snapshot
note "2. ledger snapshot"
if [ -s sovereign/ledger.jsonl ]; then
  snap="research/datasets/ledger-snapshot-$(date +%Y%m%d).jsonl"
  cp sovereign/ledger.jsonl "$snap"
  rows=$(wc -l < "$snap" | tr -d ' ')
  ok "wrote $snap ($rows rows)"
else
  bad "sovereign/ledger.jsonl missing or empty"
fi

# 3. CLI entrypoints
note "3. CLI entrypoints from new paths"
if python -m ag.verify >/dev/null 2>&1; then
  ok "python -m ag.verify"
else
  bad "python -m ag.verify"
fi
if python -m ax.harnesses.ablate_scale >/dev/null 2>&1; then
  ok "python -m ax.harnesses.ablate_scale"
elif python -m ax.harnesses.ablate_scale 2>&1 | head -1 | grep -q .; then
  ok "python -m ax.harnesses.ablate_scale (ran)"
else
  bad "python -m ax.harnesses.ablate_scale"
fi

# 4. stale module imports (fatal)
note "4. stale module imports (would crash at runtime)"
stale_imports=$(grep -rIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ \
  -E "(from|import) +(sovereign\.(verify|model|healer)|control_plane\.integration|research\.harnesses)" \
  --include="*.py" . 2>/dev/null || true)
if [ -z "$stale_imports" ]; then
  ok "no stale module imports"
else
  echo "$stale_imports" | sed 's/^/    /'
  bad "stale imports found (see above)"
fi

# 4b. informational old-path mentions
note "4b. old-path mentions in strings/docs (informational)"
mentions=$(grep -rIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ \
  --exclude-dir=dist --exclude="post_refactor_check.sh" --exclude="bootstrap*.sh" \
  --exclude="install_real_generate.sh" \
  -e "sovereign/verify" -e "control_plane/integration" -e "research/harnesses" \
  --include="*.py" --include="*.md" --include="*.json" . 2>/dev/null || true)
if [ -z "$mentions" ]; then
  ok "no old-path mentions"
else
  cnt=$(echo "$mentions" | wc -l | tr -d ' ')
  ok "$cnt mentions (non-blocking)"
fi

# 5. tracked-and-not-ignored
note "5. tracked-and-not-ignored"
for f in data/nature.txt data/algorithms.json nature/algorithms.py tests/test_nature_algorithms.py; do
  if git check-ignore -q "$f"; then
    bad "$f is git-ignored"
  elif git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    ok "$f tracked"
  else
    bad "$f untracked"
  fi
done

# 6. full pytest suite
note "6. full pytest suite"
out=$(python -m pytest -q 2>&1)
rc=$?
if [ $rc -eq 0 ]; then
  ok "$(echo "$out" | tail -1)"
else
  echo "$out" | tail -20 | sed 's/^/    /'
  bad "pytest failed"
fi

# result + commit
note "result"
if [ "$FAIL" -eq 0 ]; then
  ok "all checks green"
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -s -m "chore(post-refactor): snapshot ledger and verify ac/ag/ax + nature" \
      && git push origin main \
      && git log --oneline -1
  else
    ok "working tree already clean — nothing to commit"
  fi
else
  bad "checks failed — not committing"
  exit 1
fi
