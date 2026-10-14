# Aether Fabric Sovereign

A local-first sovereign stack: semantic layers, WORM ledger, MLX inference,
Prometheus metrics, structured logging, health probes, license audit, and
OpenTelemetry tracing. Every module has been verified against real library
APIs and has an associated test that runs on macOS.

## What is real

| Module | What it does | Tests |
|---|---|---|
| `ag/settings.py` | Lazy Pydantic v2 settings; key file validation; masked secrets | 15 |
| `ag/logging.py` | Structured JSON logs with contextvars propagation | 12 |
| `ag/metrics.py` | Prometheus with private registry; route-template labels | 17 |
| `ac/app.py` (metrics) | Real request labels; `/metrics` endpoint | 10 |
| `ag/health.py` | Subsystem probes; 503 on down | 12 |
| `ag/licenses.py` | CycloneDX SBOM audit with SPDX expression evaluation | 18 |
| `ag/tracing.py` | Fail-safe OTel with reachability check and shutdown | 13 |
| `ac/app.py` (tracing) | Per-request spans | 6 |

**Total: 285 tests passing.**

## What is not present

Six items from the original blueprint require infrastructure this repository
does not have. See `artifacts/STATUS.md`.

1. OPA policy enforcement
2. cosign / sigstore signing
3. SLSA provenance
4. Secret vault / KMS
5. Container registry
6. Certificate management

## Install

    pip install "pydantic>=2.9" "pydantic-settings>=2.4" cryptography prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc license-expression pip-licenses cyclonedx-bom httpx pyyaml

## Run

    pytest -q
    ./tooling/verify_all.sh

## Configuration

Environment variables (all prefixed `SOVEREIGN_`):

| Variable | Required | Purpose |
|---|---|---|
| `SOVEREIGN_NODE_ID` | yes (for `/healthz` 200) | Identifier for this node |
| `SOVEREIGN_ED25519_PRIVATE_KEY_PATH` | no | Ed25519 private key (0600 perms) |
| `SOVEREIGN_ENCRYPTION_SALT` | no | Base64, decoded length >= 32 bytes |
| `SOVEREIGN_TENSOR_SWARM_PORT` | no | Default 9001 |
| `SOVEREIGN_LOG_LEVEL` | no | Default INFO |
| `SOVEREIGN_LEDGER_PATH` | no | Default `sovereign/ledger.jsonl` |
| `SOVEREIGN_MODEL_PATH` | no | Default `models/tiny/model.safetensors` |
| `SOVEREIGN_TRACING` | no | `1` to enable OTel |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | no | OTLP gRPC URL |

## Endpoints

| Path | Purpose |
|---|---|
| `GET /healthz` | Subsystem health; 200 if ok, 503 if down |
| `GET /metrics` | Prometheus exposition |
| `POST /api/v1/execute` | Payload echo, instrumented |
