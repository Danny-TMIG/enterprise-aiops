# Artifact Status

## Implemented

| Family | Location | Tests |
|---|---|---|
| Configuration | `ag/settings.py` | 15 |
| Logging | `ag/logging.py` | 12 |
| Metrics | `ag/metrics.py` | 17 |
| Metrics middleware | `ac/app.py` | 10 |
| Health | `ag/health.py` | 12 |
| License audit | `ag/licenses.py` | 18 |
| Tracing | `ag/tracing.py` | 13 |
| Tracing middleware | `ac/app.py` | 6 |
| Prometheus scrape config | `tooling/prometheus.yml` | n/a |
| Capabilities schema | `schemas/capabilities.schema.yaml` | n/a |
| SBOM generator | `tooling/emit_sbom.sh` | n/a |
| CI workflow | `.github/workflows/ci.yml` | n/a |
| Env template | `.env.example` | n/a |

## Absent — infrastructure not present

1. OPA policy enforcement — needs OPA server
2. cosign / sigstore signing — needs keypair + OIDC
3. SLSA provenance — needs isolated builder
4. Secret vault / KMS — needs Vault or cloud KMS
5. Container registry — needs image pipeline
6. Certificate management — needs a CA
