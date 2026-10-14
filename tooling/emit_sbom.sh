#!/usr/bin/env bash
# Generate a real CycloneDX SBOM from the installed .venv.
#
# Requires: pip install cyclonedx-bom
#
# Output: sbom/sbom.cdx.json
#
# Then audit it:
#   python -m ag.licenses sbom/sbom.cdx.json
set -euo pipefail
cd "$HOME/aether"

if ! command -v cyclonedx-py >/dev/null 2>&1; then
  echo "cyclonedx-py not found. Install with: pip install cyclonedx-bom" >&2
  exit 1
fi

mkdir -p sbom
OUT="sbom/sbom.cdx.json"

echo "[*] Generating SBOM from .venv ..."
cyclonedx-py environment --output-format json -o "$OUT"

N=$(python3 -c "import json; print(len(json.load(open('$OUT')).get('components', [])))")
echo "[*] Wrote $OUT ($N components)"
echo
echo "[*] Running license audit ..."
python3 -m ag.licenses "$OUT" || true
