# dcs-conformance

Belnap-folded conformance for the modern compliance stack.

Binary tools answer pass/fail. When two of them disagree — GitHub says
yes, AWS says no, an auditor says "partial" — they have no state for it.
`dcs` does.

## Install

    pip install dcs-conformance

Optional extras:

    pip install 'dcs-conformance[aws]'      # boto3 connector
    pip install 'dcs-conformance[oscap]'    # OpenSCAP ARF parsing
    pip install 'dcs-conformance[crypto]'   # Ed25519 signing

## Quickstart

    dcs keygen          # generate dcs/key.hex (Ed25519, gitignored)
    dcs self            # fold local tests x external sources

Every run writes three files:

- self-<ts>.json         primary signed bundle
- self-<ts>.oscal.json   OSCAL 1.1.2 Assessment Results
- self-<ts>.intoto.json  in-toto v1 Statement in a DSSE envelope

## Verify

    dcs verify-intoto dcs/evidence/self-<ts>.intoto.json
    # OK: 1 valid signature(s)

Or against an externally supplied public key:

    dcs verify-intoto envelope.json --pubkey $(cat dcs/key.pub.hex)

## The Belnap fold

Each requirement gets attestations from multiple sources. They fold
via meet over Belnap FOUR:

| sources              | folded |
|----------------------|--------|
| local=T, github=T    | T      |
| local=T, aws=F       | B      |
| local=T, github=U    | T      |
| all=F                | F      |

CONFLICT is a first-class state. A binary tool would have printed one
of the inputs and dropped the disagreement.

## Connectors

Sovereign plugins. Missing tool or missing env var yields U; the
verdict narrows but never breaks.

- github      README, workflows, default branch
- aws         S3 encryption, CloudTrail multi-region, IAM password policy
- oscap       OpenSCAP ARF XML
- kube_bench  CIS Kubernetes Benchmark
- kyverno     Kyverno PolicyReport CRDs
- prowler     Prowler OCSF findings

## Interoperability

- OSCAL       consumed by compliance-trestle, trestle-cli, FedRAMP tooling
- in-toto     consumed by cosign, Rekor, policy-controller
- Ed25519     verifiable with only key.pub.hex

## License

Apache-2.0
