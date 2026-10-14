#!/usr/bin/env bash
# One-shot: regenerate the spec-to-code map, run status, run tests.
# Idempotent. Read-only with respect to components/.
set -euo pipefail
cd "$(dirname "$0")/../.."

echo "== generate spec-to-code map =="
python3 tooling/validation/generate_spec_to_code.py

echo
echo "== status =="
python3 tooling/validation/status.py || true

echo
echo "== full-stack diagnostic =="
make test || true

echo
echo "done."
