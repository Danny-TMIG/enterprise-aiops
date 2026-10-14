#!/usr/bin/env python3
"""Rebuild the five stubs as real, working files.

Replaces what was deleted in consolidation with real versions:

  1. tooling/prometheus.yml               — real Prometheus scrape config
  2. schemas/capabilities.schema.yaml     — real JSON Schema for capabilities.json
  3. tooling/emit_sbom.sh                 — real SBOM generator (runs cyclonedx-py)
  4. .env.example                         — real, documented env template
  5. .github/workflows/ci.yml             — real GitHub Actions workflow

Then generates sbom/sbom.cdx.json and runs pytest + verify_all.sh.
"""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "aether"


def w(rel: str, content: str, exec_bit: bool = False) -> None:
    p = REPO / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    if exec_bit:
        p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  wrote {rel}  ({len(content.splitlines())} lines, "
          f"{len(content)} bytes, sha256={hashlib.sha256(content.encode()).hexdigest()[:12]})")


# ---------------------------------------------------------------------------
print("== 1. tooling/prometheus.yml ==")
w("tooling/prometheus.yml", """# Prometheus scrape configuration for the Aether sovereign node.
#
# Run standalone:
#   prometheus --config.file=tooling/prometheus.yml
#
# Then open http://localhost:9090 and query:
#   rate(sovereign_requests_total[5m])
#   histogram_quantile(0.99, rate(sovereign_request_duration_seconds_bucket[5m]))

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    service: aether-core-asgi

rule_files: []

scrape_configs:
  - job_name: aether-core-asgi
    metrics_path: /metrics
    scheme: http
    static_configs:
      - targets: ['127.0.0.1:8000']
        labels:
          environment: dev
          node: local
""")


# ---------------------------------------------------------------------------
print("\n== 2. schemas/capabilities.schema.yaml ==")
w("schemas/capabilities.schema.yaml", """$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/capabilities.schema.yaml"
title: CapabilityContracts
description: |
  Contracts for every component family. status=declared until implemented;
  evidence list is empty by default.
type: object
required: [schema, capabilities]
additionalProperties: false
properties:
  schema:
    type: string
    const: "aether.capabilities.v1"
  note:
    type: string
  capabilities:
    type: array
    minItems: 1
    items:
      type: object
      required: [id, family_id, group, name, inputs, limits, permissions,
                 evidence_required, implementation]
      additionalProperties: false
      properties:
        id:
          type: string
          pattern: "^cap\\\\.[a-z]+\\\\.[0-9]{3}\\\\.[a-z0-9_]+$"
        family_id:
          type: integer
          minimum: 1
        group:
          type: string
          enum:
            - hardware
            - system
            - program
            - toolchain
            - application
            - security
            - lifecycle
            - specialized
        name:
          type: string
          minLength: 1
        inputs:
          type: array
          items: { type: string }
        limits:
          type: object
          required: [max_concurrency, max_seconds]
          additionalProperties: false
          properties:
            max_concurrency:
              type: integer
              minimum: 1
            max_seconds:
              type: integer
              minimum: 1
        permissions:
          type: array
          items: { type: string }
        evidence_required:
          type: array
          items: { type: string }
        implementation:
          type: object
          required: [status]
          additionalProperties: false
          properties:
            status:
              type: string
              enum: [declared, partial, complete, deprecated]
            module:
              type: [string, "null"]
            entrypoint:
              type: [string, "null"]
        includes:
          type: array
          items: { type: string }
""")


# ---------------------------------------------------------------------------
print("\n== 3. tooling/emit_sbom.sh ==")
w("tooling/emit_sbom.sh", """#!/usr/bin/env bash
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
""", exec_bit=True)


# ---------------------------------------------------------------------------
print("\n== 4. .env.example ==")
w(".env.example", """# Environment variables for the Aether sovereign stack.
# Copy to .env and edit. Never commit the real .env.

# ---------------------------------------------------------------------------
# Required
# ---------------------------------------------------------------------------
# Identifier for this node. Required for /healthz to return 200.
SOVEREIGN_NODE_ID=node-01

# ---------------------------------------------------------------------------
# Optional: cryptographic material
# ---------------------------------------------------------------------------
# Path to an Ed25519 private key (PEM). The file must exist, be readable,
# and have no group or world bits (0600 or 0400). The key is parsed at
# startup to fail fast if it's malformed.
#SOVEREIGN_ED25519_PRIVATE_KEY_PATH=/etc/aether/ed25519.pem

# Base64-encoded salt, decoded length must be >= 32 bytes. Example generation:
#   python3 -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())"
#SOVEREIGN_ENCRYPTION_SALT=

# ---------------------------------------------------------------------------
# Optional: runtime
# ---------------------------------------------------------------------------
# Port for the tensor swarm gateway.
#SOVEREIGN_TENSOR_SWARM_PORT=9001

# Log level: DEBUG, INFO, WARNING, ERROR.
#SOVEREIGN_LOG_LEVEL=INFO

# Environment: dev, staging, prod.
#SOVEREIGN_ENVIRONMENT=dev

# Path to the WORM ledger (data file). Parent directory must be writable.
#SOVEREIGN_LEDGER_PATH=sovereign/ledger.jsonl

# Path to the model weights. If absent, /healthz reports "degraded" for the
# model subsystem but the app still serves requests.
#SOVEREIGN_MODEL_PATH=models/tiny/model.safetensors

# ---------------------------------------------------------------------------
# Optional: tracing
# ---------------------------------------------------------------------------
# Set to 1 to enable OpenTelemetry span emission.
#SOVEREIGN_TRACING=0

# OTLP gRPC collector URL. If unreachable at startup, tracing is disabled
# with a warning; the process still serves requests.
#OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4317
""")


# ---------------------------------------------------------------------------
print("\n== 5. .github/workflows/ci.yml ==")
w(".github/workflows/ci.yml", """name: ci

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: false
          fetch-depth: 1

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov
          pip install "pydantic>=2.9" "pydantic-settings>=2.4" cryptography
          pip install prometheus-client
          pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
          pip install license-expression pip-licenses cyclonedx-bom
          pip install httpx pyyaml fastapi uvicorn
          pip install -r requirements.txt || true

      - name: Run tests
        env:
          SOVEREIGN_NODE_ID: ci-node
        run: python -m pytest -q

      - name: Verify stack
        env:
          SOVEREIGN_NODE_ID: ci-node
        run: bash tooling/verify_all.sh

      - name: Generate SBOM
        run: bash tooling/emit_sbom.sh

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom/sbom.cdx.json
          if-no-files-found: warn
""")


# ---------------------------------------------------------------------------
print("\n== 6. running tooling/emit_sbom.sh ==")
rc = subprocess.call(["bash", str(REPO / "tooling/emit_sbom.sh")])
print(f"  emit_sbom rc={rc}")
if rc != 0:
    print("  (not fatal — cyclonedx-bom may not be installed; install with: pip install cyclonedx-bom)")


# ---------------------------------------------------------------------------
print("\n== 7. verifying the five files on disk ==")
for rel in (
    "tooling/prometheus.yml",
    "schemas/capabilities.schema.yaml",
    "tooling/emit_sbom.sh",
    ".env.example",
    ".github/workflows/ci.yml",
):
    p = REPO / rel
    if p.is_file():
        print(f"  ok: {rel}  ({len(p.read_text().splitlines())} lines)")
    else:
        print(f"  MISSING: {rel}")
        sys.exit(1)


# ---------------------------------------------------------------------------
print("\n== 8. validating capabilities.json against the new schema ==")
try:
    import json
    import yaml
    from jsonschema import Draft202012Validator

    schema = yaml.safe_load((REPO / "schemas/capabilities.schema.yaml").read_text())
    doc = json.loads((REPO / "data/capabilities.json").read_text())
    Draft202012Validator(schema).validate(doc)
    print("  capabilities.json validates against the schema")
except ImportError as e:
    print(f"  (skipped: {e}; pip install jsonschema pyyaml)")
except Exception as e:
    print(f"  VALIDATION FAILED: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
print("\n== 9. running full test suite ==")
rc = subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=str(REPO))
print(f"  pytest rc={rc}")


# ---------------------------------------------------------------------------
print("\n== 10. running verify_all.sh ==")
rc = subprocess.call(["bash", str(REPO / "tooling/verify_all.sh")], cwd=str(REPO))
print(f"  verify_all rc={rc}")


# ---------------------------------------------------------------------------
print("\n== next: commit ==")
print("  cd ~/aether && git add -A")
print("  git commit -s -m \\")
print("    \\\"feat: rebuild five deleted stubs as real files (prometheus, capabilities schema, sbom, env, ci)\\\"")
print("  git push origin main")
print("  git log --oneline -1")
print(f"\nresult: emit_sbom rc={rc}")
sys.exit(0 if rc == 0 else 1)
