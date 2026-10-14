#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

echo "== working tree =="
du -sh . 2>/dev/null

echo
echo "== top-level entries (largest first) =="
du -sh * .[!.]* 2>/dev/null | sort -rh | head -30

echo
echo "== git objects =="
git count-objects -vH

echo
echo "== .git dir =="
du -sh .git 2>/dev/null

echo
echo "== tracked file content =="
git ls-tree -r -l HEAD | awk '{sum+=$4} END {printf "%.2f MiB across %d files\n", sum/1024/1024, NR}'

echo
echo "== venv (if present) =="
[ -d .venv ] && du -sh .venv || echo absent

echo
echo "== tracked files =="
git ls-files | wc -l | tr -d ' '

echo
echo "== fresh shallow clone size =="
tmp=$(mktemp -d)
git clone -q --depth=1 "$(git remote get-url origin)" "$tmp/clone"
printf "clone total: %s\n" "$(du -sh "$tmp/clone" | cut -f1)"
printf "clone .git:  %s\n" "$(du -sh "$tmp/clone/.git" | cut -f1)"
printf "clone files: %s\n" "$(find "$tmp/clone" -type f -not -path '*/.git/*' | wc -l | tr -d ' ')"
rm -rf "$tmp"
