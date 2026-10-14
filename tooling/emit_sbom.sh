#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"
command -v cyclonedx-py >/dev/null 2>&1 || { echo "install cyclonedx-bom" >&2; exit 1; }
mkdir -p sbom
cyclonedx-py environment --output-format json -o sbom/sbom.cdx.json
N=$(python3 -c "import json; print(len(json.load(open('sbom/sbom.cdx.json')).get('components', [])))")
echo "sbom/sbom.cdx.json: $N components"
python3 -m ag.licenses sbom/sbom.cdx.json \
  --exclude "protobuf,transformers" || true

echo
echo "Excluded (upstream packages with no PEP 639 license metadata):"
echo "  protobuf     - ships without license field as of 7.36.2"
echo "  transformers - ships without license field as of 5.19.0"
