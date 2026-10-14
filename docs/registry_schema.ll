;; artifact: registry_schema
FILE registries/SCHEMA.md
# Registry Envelope

Uniform schema across all eight registry kinds.

    id: <registry>://<namespace>/<name>@<version>
    kind: code | types | operators | specs | gates | evidence | manifold | provenance
    name: <string>
    version: <semver>
    schema_version: <semver>
    license: <SPDX>
    owner: <human | org>
    homepage: <url>
    source: <vcs-url>
    published: <timestamp>
    dependencies:
      - id: <registry>://<namespace>/<name>@<range>
        kind: <registry-kind>
    interfaces:
      provides: [<type-id>, <operator-id>, <spec-id>, <gate-id>]
      requires: [<type-id>, <operator-id>, <spec-id>, <gate-id>]
    signatures:
      - signer: <identity>
        method: sigstore | gpg | minisign
        value: <base64>
    attestations:
      - type: slsa-level
        value: 3
      - type: reproducibility
        value: hermetic
    aovs:
      coverage_spec: 0.0..1.0
      coverage_test: 0.0..1.0
      coverage_type: 0.0..1.0
      faithfulness:  0.0..1.0
      consistency:   0.0..1.0
ENDFILE registries/SCHEMA.md
