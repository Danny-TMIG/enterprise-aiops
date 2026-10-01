#!/usr/bin/env bash
# Copy canonical core.py and mesh.py into app/train/, then verify invariants.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD"

cp tools/hooks/canonical_core.py app/train/core.py
cp tools/hooks/canonical_mesh.py app/train/mesh.py
echo "sync: files written"

python3 tools/hooks/invariants.py
