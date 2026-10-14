;; artifact: manifest_example
FILE examples/auth/manifest.yaml
library: acme/auth
version: 2.3.1
entries:
  code:       code://acme/auth@2.3.1
  types:      types://acme/auth@2.3.1
  operators:  operators://acme/auth-ops@2.3.1
  specs:      specs://acme/auth-spec@2.3.1
  gates:      gates://acme/auth-gates@2.3.1
  evidence:   evidence://acme/auth-soc2@2.3.1
  provenance: provenance://acme/auth-slsa@2.3.1
faces:
  - spec: SPEC-0001
  - spec: SPEC-0002
  - gate_bundle: GATE-ASVS
  - gate_bundle: GATE-AISVS
integrity:
  iec_61508: SIL-1
  iso_26262: ASIL-A
regulations: [gdpr-32, owasp-aisvs-l2]
ENDFILE examples/auth/manifest.yaml
