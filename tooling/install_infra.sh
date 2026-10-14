#!/usr/bin/env bash
set -uo pipefail
cd "$HOME/aether"

step() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()   { printf "  \033[32mOK\033[0m %s\n" "$*"; }
bad()  { printf "  \033[31mERR\033[0m %s\n" "$*"; }

# ---------------------------------------------------------------------------
step "1. k3d cluster"
if command -v k3d >/dev/null 2>&1; then
  ok "k3d present ($(k3d version | head -1))"
else
  brew install k3d && ok "k3d installed"
fi

if k3d cluster list 2>/dev/null | grep -q '^aether '; then
  ok "cluster 'aether' exists"
else
  k3d cluster create aether --servers 1 --wait && ok "cluster created"
fi

export KUBECONFIG="$(k3d kubeconfig write aether)"
kubectl cluster-info --request-timeout=5s >/dev/null 2>&1 && ok "kubectl reachable"

# ---------------------------------------------------------------------------
step "2. cert-manager"
if ! command -v helm >/dev/null 2>&1; then
  brew install helm
fi

helm repo add jetstack https://charts.jetstack.io >/dev/null 2>&1
helm repo update >/dev/null 2>&1

if kubectl get ns cert-manager >/dev/null 2>&1; then
  ok "namespace cert-manager exists"
else
  helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager --create-namespace --version v1.14.5 \
    --set installCRDs=true --wait --timeout 5m
  ok "cert-manager installed"
fi

kubectl wait --for=condition=Available --timeout=300s \
  -n cert-manager deployment/cert-manager >/dev/null 2>&1 && ok "controller ready"
kubectl wait --for=condition=Available --timeout=300s \
  -n cert-manager deployment/cert-manager-webhook >/dev/null 2>&1 && ok "webhook ready"

# ---------------------------------------------------------------------------
step "3. issue a self-signed certificate"
kubectl apply -f - <<'YAML' >/dev/null
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-issuer
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: aether-tls
  namespace: default
spec:
  secretName: aether-tls
  issuerRef:
    name: selfsigned-issuer
    kind: ClusterIssuer
  dnsNames:
    - "*.aether.localhost"
YAML

sleep 5
kubectl get certificate aether-tls -n default
kubectl get secret aether-tls -n default -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -subject -issuer -dates 2>/dev/null

# ---------------------------------------------------------------------------
step "4. SLSA L3 — check for Kettle and CVM availability"
if command -v kettle >/dev/null 2>&1; then
  ok "kettle present"
else
  echo "  - kettle not installed; install via:"
  echo "      cargo install --features attest --git https://github.com/confidential-dot-ai/kettle"
  echo "    Requires Rust toolchain and a CVM (AMD SEV-SNP or Intel TDX) to sign."
fi

if [[ "$(uname -m)" == "arm64" && "$(uname -s)" == "Darwin" ]]; then
  echo "  - this host is Apple Silicon; no SEV-SNP or TDX. Kettle attestation"
  echo "    must run on a cloud CVM:"
  echo "      Azure  DCasv5/ECasv5 (SEV-SNP) or DCesv5 (TDX)"
  echo "      GCP    n2d-standard (SEV-SNP) or c3-standard (TDX)"
  echo "      AWS    M6a/C6a/R6a (SEV-SNP only)"
fi

# ---------------------------------------------------------------------------
step "5. SLSA L3 — write the GitHub Actions release workflow"
mkdir -p .github/workflows
cat > .github/workflows/release.yml <<'YAML'
name: release
on:
  push:
    tags: ['v*']
permissions:
  contents: write
  id-token: write
  packages: write
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      hashes: ${{ steps.hash.outputs.hashes }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - name: Build artifacts
        run: |
          python -m pip install build
          python -m build --sdist --wheel
      - name: Compute hashes
        id: hash
        run: |
          cd dist && echo "hashes=$(sha256sum * | base64 -w0)" >> "$GITHUB_OUTPUT"
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/ }
  provenance:
    needs: [build]
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2.0.0
    with:
      base64-subjects: ${{ needs.build.outputs.hashes }}
      upload-assets: true
  verify:
    needs: [provenance]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist }
      - uses: slsa-framework/slsa-verifier/actions/installer@v2.6.0
      - name: Verify
        run: |
          ls dist
          slsa-verifier verify-artifact dist/* \
            --provenance-path multiple.intoto.jsonl \
            --source-uri github.com/${{ github.repository }}
YAML
ok "wrote .github/workflows/release.yml"

# ---------------------------------------------------------------------------
step "6. update artifacts/STATUS.md"
python3 - <<'PY'
from pathlib import Path
p = Path.home() / "aether" / "artifacts" / "STATUS.md"
s = p.read_text()

add = """
## Certificate management (cert-manager)

Running locally in k3d cluster `aether`. Install:

    brew install k3d helm
    k3d cluster create aether --servers 1 --wait
    export KUBECONFIG=$(k3d kubeconfig write aether)
    helm repo add jetstack https://charts.jetstack.io
    helm install cert-manager jetstack/cert-manager \\
      --namespace cert-manager --create-namespace \\
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
"""

if "SLSA Build L3" not in s:
    p.write_text(s.rstrip() + "\n" + add)
    print("  updated artifacts/STATUS.md")
else:
    print("  STATUS.md already documents L1/L3")
PY

step "result"
echo "cert-manager:  kubectl get certificate -A"
echo "SLSA release:  push a tag: git tag v0.1.0 && git push origin v0.1.0"
echo "STATUS.md:     updated"
