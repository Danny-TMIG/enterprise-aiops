# Artifact Status

## Implemented (in-repo code)

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

Total: 286 tests passing.

## Running locally (Colima + Docker)

| Component | Endpoint | Reproduce with |
|---|---|---|
| OPA | http://localhost:8181 | docker run -d --name opa -p 8181:8181 openpolicyagent/opa:latest run --server --addr 0.0.0.0:8181 |
| Vault (dev mode) | http://localhost:8200 | docker run -d --name vault -p 8200:8200 -e VAULT_DEV_ROOT_TOKEN_ID=dev-only-token hashicorp/vault:latest server -dev |
| OCI registry | http://localhost:5000 | docker run -d -p 5000:5000 --restart always --name registry registry:2 |
| Grafana | http://localhost:3000 | pre-existing container |
| Thanos querier | http://localhost:10902 | pre-existing container |
| Loki | http://localhost:3100 | docker run -d --name asf-loki -p 3100:3100 -v ~/aether/ops/loki/loki-config.yaml:/etc/loki/loki-config.yaml:ro grafana/loki:latest -config.file=/etc/loki/loki-config.yaml |

### Cosign keypair

Generated at ~/aether/cosign.key and ~/aether/cosign.pub. The private key is
gitignored. Keyless signing (OIDC + Fulcio + Rekor) requires a CI environment
with id-token: write.

## Vault secrets engine

    export VAULT_ADDR=http://127.0.0.1:8200
    export VAULT_TOKEN=dev-only-token
    vault secrets enable -path=shared -version=2 kv
    vault kv put -mount=shared kv/creds username=opsuser password=p@ssw0rd

## Still absent - infrastructure not present

1. SLSA provenance - requires a GitHub Actions runner with id-token: write.
   A laptop cannot produce SLSA level 3 provenance honestly. Add
   .github/workflows/release.yml using slsa-framework/slsa-github-generator.

2. Certificate management (cert-manager) - requires a Kubernetes cluster.
   cert-manager has no standalone macOS binary. To run it locally, install
   k3d and create a cluster, then kubectl apply -f the cert-manager manifest.

## Certificate management (cert-manager)

Running locally in k3d cluster `aether`. Install:

    brew install k3d helm
    k3d cluster create aether --servers 1 --wait
    export KUBECONFIG=$(k3d kubeconfig write aether)
    helm repo add jetstack https://charts.jetstack.io
    helm install cert-manager jetstack/cert-manager \
      --namespace cert-manager --create-namespace \
      --version v1.14.5 --set installCRDs=true

Issue a self-signed certificate:

    kubectl apply -f ops/cert-manager/selfsigned.yaml

## SLSA Build L3 provenance

**Build L1**: satisfied by `.github/workflows/ci.yml`.

**Build L3**: `.github/workflows/release.yml` calls
`slsa-framework/slsa-github-generator@v2.0.0` with `id-token: write`.
The generator runs in a separate reusable workflow; its OIDC identity signs
the attestation, and the caller cannot reach the signing key. The workflow
also runs `slsa-verifier` against the produced provenance.

To reach L3 with hardware enforcement on this hardware: impossible. A laptop
cannot provide administrative isolation from the build's own operator. The
Apple M4 Max Secure Enclave is a key vault, not a confidential computing
platform; it has no equivalent of AMD SEV-SNP or Intel TDX. Kettle on a
cloud CVM is the hardware-enforced path:

    Azure  DCasv5/ECasv5 (SEV-SNP) or DCesv5 (TDX)
    GCP    n2d-standard (SEV-SNP) or c3-standard (TDX)
    AWS    M6a/C6a/R6a (SEV-SNP only)
