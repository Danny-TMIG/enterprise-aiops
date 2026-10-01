#!/usr/bin/env bash
# After /tmp/parallel_train.py runs, ensure core.py and mesh.py match canonical.
set -uo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD"

python3 tools/hooks/fix_cli.py || true
bash tools/hooks/sync.sh
rc=$?
if [ $rc -ne 0 ]; then
  echo "post_regen: invariants FAILED (sync rc=$rc)"
  exit $rc
fi
echo "post_regen: OK"
