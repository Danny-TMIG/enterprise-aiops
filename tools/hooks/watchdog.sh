#!/usr/bin/env bash
# Check invariants. On failure, heal from canonical and re-check.
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD"

if python3 tools/hooks/invariants.py >/dev/null 2>&1; then
    echo "watchdog: OK"
    exit 0
fi
echo "watchdog: invariants broken — healing"
bash tools/hooks/sync.sh
