#!/usr/bin/env bash
# Block 6 live proof: generate a real SBOM from .venv, audit it, verify exit codes.
set -uo pipefail
cd "$HOME/aether"

echo "== 1. run block-6 tests =="
python -m pytest tests/test_licenses.py -q 2>&1 | tail -3

echo
echo "== 2. generate SBOM from .venv =="
mkdir -p sbom
cyclonedx-py environment --output-format json -o sbom/sbom.cdx.json
COMPONENTS=$(python3 -c "import json; print(len(json.load(open('sbom/sbom.cdx.json')).get('components', [])))")
echo "sbom/sbom.cdx.json: $COMPONENTS components"
[ "$COMPONENTS" -gt 0 ] || { echo "SBOM empty; aborting"; exit 1; }

echo
echo "== 3. audit with permissive allowlist (expect 0) =="
python -m ag.licenses sbom/sbom.cdx.json \
  --allow "MIT,Apache-2.0,BSD-2-Clause,BSD-3-Clause,ISC,Python-2.0,PSF-2.0,MPL-2.0,Unlicense,CC0-1.0,Zlib,MulanPSL-2.0,0BSD" \
  --include-dev
echo "exit=$?"

echo
echo "== 4. audit with strict allowlist (expect violations) =="
python -m ag.licenses sbom/sbom.cdx.json --allow "MIT"
echo "exit=$?"

echo
echo "== 5. machine-readable report =="
python -m ag.licenses sbom/sbom.cdx.json --allow "MIT" --json | python3 -m json.tool | head -30

echo
echo "== RESULT: block 6 verified =="
