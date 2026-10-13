#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/enterprise_aiops}"
DB="${2:-$HOME/enterprise_aiops/dcs_codeql/db}"

if ! command -v codeql >/dev/null 2>&1 && ! gh codeql version >/dev/null 2>&1; then
  echo "codeql CLI not found. Install: gh extension install github/gh-codeql"
  exit 2
fi

# prefer gh codeql if codeql is not on PATH
if command -v codeql >/dev/null 2>&1; then
  CQL=codeql
else
  CQL="gh codeql"
fi

if [ ! -d "$DB" ]; then
  echo "→ building CodeQL database for $TARGET"
  mkdir -p "$(dirname "$DB")"
  rm -rf "$DB"
  $CQL database create "$DB" \
    --language=python \
    --source-root="$TARGET" \
    --overwrite \
    > /dev/null 2>&1
  echo "  database built: $DB"
else
  echo "→ reusing existing database: $DB"
fi

echo
echo "→ running grounding queries"
PASS=0
FAIL=0
for q in queries/*.ql; do
  name=$(basename "$q" .ql)
  out=$(mktemp)
  if ! $CQL query run --database="$DB" --output="$out" "$q" >/dev/null 2>&1; then
    echo "  ERROR $name  (query failed to run)"
    FAIL=$((FAIL + 1))
    rm -f "$out"
    continue
  fi
  txt=$(mktemp)
  $CQL bqrs decode --format=csv "$out" > "$txt" 2>/dev/null || true
  # count data rows = lines - 1 (header). Guard against empty file.
  total=$(wc -l < "$txt" | tr -d ' \n')
  total=${total:-0}
  if [ "$total" -le 0 ]; then
    rows=0
  else
    rows=$((total - 1))
  fi
  if [ "$rows" -le 0 ]; then
    echo "  PASS  $name  (0 violations)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name  ($rows violations)"
    head -3 "$txt"
    FAIL=$((FAIL + 1))
  fi
  rm -f "$out" "$txt"
done

echo
echo "════════════════════════════════════════"
echo "  grounded claims passing: $PASS / 8"
echo "  grounded claims failing: $FAIL / 8"
echo "════════════════════════════════════════"
[ "$FAIL" -eq 0 ]
