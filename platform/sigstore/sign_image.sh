#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:?usage: sign_image.sh <image:tag>}"
cosign sign --yes "$IMAGE"
cosign attest --yes --predicate platform/sigstore/sbom.spdx.json "$IMAGE"
