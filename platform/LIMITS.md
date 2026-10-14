# platform/ — what is declared vs what runs on this host

This directory is a **declaration tree**, not a running RHEL installation.

| Artifact | On this Mac | On a RHEL 10 CI runner |
|----------|-------------|------------------------|
| `platform/rhel/substrate.json` | parsed by `make platform-validate` | source of truth for image build |
| `platform/rhel/kickstart/*.ks` | linted for shell syntax | fed to `anaconda` |
| `platform/rhel/system-roles/*.yml` | `ansible-lint` + `yamllint` | applied by AAP 2.6 |
| `platform/ansible/playbooks/*.yml` | `ansible-lint` | executed against `asf_nodes` |
| `platform/ansible/rulebooks/*.yml` | `yamllint` | loaded by Event-Driven Ansible |
| `platform/openshift/**` | `yamllint` + `check-jsonschema` | `oc apply -k` on an OpenShift cluster |
| `platform/scap/baselines/*.json` | `check-jsonschema` | consumed by `oscap xccdf eval` |
| `platform/sigstore/*.sh` | `shellcheck` | signs against a live registry with cosign |
| `platform/rhel` | listed | executed |
| `platform/ansible` | listed | executed |
| `platform/openshift` | listed | executed |
| `platform/scap` | listed | executed |
| `platform/sigstore` | listed | executed |

`make platform-validate` runs the "On this Mac" column only. It **fails loudly** if any file is malformed. It never claims `oscap`, `dnf`, `oc`, `subscription-manager`, or `cosign sign` were executed.

To run the "On a RHEL 10 CI runner" column:
1. Provision a RHEL 10 host with an active subscription.
2. Install `ansible-core`, `ansible-lint`, `oscap`, `scap-security-guide`, `rhel-system-roles`, `podman`, `cosign`.
3. Point `ANSIBLE_INVENTORY` at `platform/ansible/inventory/production.yml`.
4. `ansible-playbook platform/ansible/playbooks/site.yml`.
5. `make platform-scan` (defined on the RHEL host, not here).
