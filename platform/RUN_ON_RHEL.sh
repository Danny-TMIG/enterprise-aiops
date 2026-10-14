#!/usr/bin/env bash
# RUN_ON_RHEL.sh — execute every platform/ artifact that macOS cannot run.
# Copy this file to a RHEL 10 host with an active subscription, then run it.
set -euo pipefail

echo "== [1/6] register with subscription-manager =="
sudo subscription-manager register || echo "  (already registered or offline)"
sudo subscription-manager attach --auto
sudo dnf repolist | head -20

echo "== [2/6] install platform tools =="
sudo dnf install -y \
  ansible-core rhel-system-roles \
  openscap-scanner scap-security-guide \
  podman keylime tpm2-tools

echo "== [3/6] run OpenSCAP CIS L1 scan with remediation =="
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
  --remediate --report /var/tmp/oscap-cis-l1.html \
  /usr/share/xml/scap/ssg/content/ssg-rhel10-ds.xml || true

echo "== [4/6] run OpenSCAP STIG V1R2 scan =="
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_stig \
  --report /var/tmp/oscap-stig.html \
  /usr/share/xml/scap/ssg/content/ssg-rhel10-ds.xml || true

echo "== [5/6] apply system-roles + deploy units with Ansible =="
cd "$(dirname "$0")/.."
ansible-playbook -i platform/ansible/inventory/production.yml \
  platform/ansible/playbooks/site.yml

echo "== [6/6] optional: OpenShift + Keylime + Sigstore =="
cat <<'HINT'
  OpenShift Local (single-node):
    curl -LO https://developers.redhat.com/content-gateway/file/pub/openshift-v4/clients/crc/latest/crc-linux-amd64.tar.xz
    tar xf crc-linux-amd64.tar.xz
    sudo install -m 0755 crc-linux-*-amd64/crc /usr/local/bin/crc
    crc setup && crc start -p pull-secret.txt
    eval $(crc oc-env)
    oc apply -f platform/openshift/gitops/overlays/governance/application.yaml

  Keylime TEE attestation (requires TPM 2.0):
    sudo systemctl enable --now keylime_verifier keylime_registrar keylime_agent
    keylime_tenant --command add --targethost 127.0.0.1 --uuid d432fbb3-d2f1-4a97-9ef7-75bd81c00000 \
      --cert default --runtime-policy runtime-policy.json --mb-policy mb-policy.json
    keylime_tenant --command cvstatus --uuid d432fbb3-d2f1-4a97-9ef7-75bd81c00000

  Sigstore signing (needs a live registry):
    cosign generate-key-pair
    platform/sigstore/sign_image.sh ghcr.io/danny-tmig/asf-governance-cell:latest
HINT

echo "== RHEL side complete — ARF/HTML reports in /var/tmp/oscap-*.html =="
