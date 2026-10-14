# Artifact Status

## Implemented

| Family | Location | Tests |
|---|---|---|
| Configuration | `ag/settings.py` | 15 |
| Structured logging | `ag/logging.py` | 12 |
| Metrics | `ag/metrics.py` | 17 |
| Metrics middleware | `ac/app.py` | 10 |
| Health probes | `ag/health.py` | 12 |
| License audit | `ag/licenses.py` | 18 |
| Tracing | `ag/tracing.py` | 13 |
| Tracing middleware | `ac/app.py` | 6 |
| WORM ledger | `ag/ledger.py` | existing |
| Model backend | `ax/model.py` | existing |
| Nature catalog | `nature/`, `data/` | 13 |

## Absent — infrastructure not present

1. OPA policy enforcement — needs OPA sidecar and JWT decoder
2. cosign / sigstore signing — needs OIDC identity and keypair
3. SLSA provenance — needs isolated builder
4. Secret vault / KMS — needs Vault or AWS/GCP KMS
5. Container registry — needs image pipeline
6. Certificate management — needs a CA

Each is documented rather than stubbed.

## Deleted superseded stubs

| Path | Superseded by |
|---|---|
| `artifacts/metrics/metrics.yaml` | `ag/metrics.py` |
| `artifacts/capabilities/cap.example.yaml` | `data/capabilities.json` |
| `artifacts/evidence/attestation.json` | deleted; no signer |
| `artifacts/provenance/slsa.json` | deleted; no builder |
| `artifacts/sbom/cyclonedx.json` | `sbom/sbom.cdx.json` |
| `artifacts/secrets/.env.example` | `ag/settings.py` |
| `artifacts/policies/policy.rego` | deleted; no OPA |
| `artifacts/alerts/alerts.yaml` | deleted; no alert manager |
| `artifacts/dashboards/overview.json` | deleted; no dashboard |
| `artifacts/ci/ci.yml` | `.github/workflows/` |
