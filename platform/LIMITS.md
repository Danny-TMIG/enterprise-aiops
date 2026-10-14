# platform/ — declared vs executable

| Artifact | macOS (this host) | RHEL 10 host |
|----------|-------------------|--------------|
| platform/rhel/substrate.json | parsed | source of truth for image build |
| platform/rhel/kickstart/*.ks | shell-syntax linted | anaconda |
| platform/rhel/system-roles/*.yml | yamllint | AAP 2.6 |
| platform/ansible/** | yamllint + shellcheck | ansible-playbook |
| platform/openshift/** | yamllint | oc apply -k |
| platform/scap/baselines/*.json | check-jsonschema | oscap xccdf eval |
| platform/sigstore/*.sh | shellcheck | cosign sign |

Directories in this tree: platform/rhel, platform/ansible, platform/openshift, platform/scap, platform/sigstore.

`make platform-validate` runs the left column only. It never claims
oscap, dnf, subscription-manager, oc, or cosign were executed.

Run `platform/RUN_ON_RHEL.sh` on a RHEL 10 host to execute the right column.
