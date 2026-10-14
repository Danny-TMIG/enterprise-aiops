#!/usr/bin/env bash
# Declared-only on macOS: requires a live registry and cosign key material.
set -euo pipefail
IMAGE="${1:?usage: sign_image.sh <image:tag>}"
cosign sign --yes "$IMAGE"
cosign attest --yes --predicate platform/sigstore/sbom.spdx.json "$IMAGE"
