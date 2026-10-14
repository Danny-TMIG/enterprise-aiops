#!/usr/bin/env bash
# Snapshot app/train before regen. Cheap; keeps last 10 snapshots.
set -euo pipefail
cd "$(dirname "$0")/../.."
D=".snapshots/$(date +%s)"
mkdir -p "$D"
cp -R app/train "$D/"
ls -1dt .snapshots/*/ | tail -n +11 | xargs -I{} rm -rf "{}" 2>/dev/null || true
echo "pre_regen: snapshot at $D"
