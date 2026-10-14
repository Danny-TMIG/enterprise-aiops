# Architecture

Aether Fabric is organized into three constitutional layers.

## AX — Aether Cognition (21 components)

- Interface: COG-INT-*
- Core: COG-CORE-*
- Reasoning: COG-REA-*
- Composition: COG-CMP-*
- Assurance: COG-ASSUR-*

## AG — Aether Govern (24 components)

- Kernel: GOV-KRN-*
- Identity: GOV-IAM-*
- Policy: GOV-POL-*
- Information: GOV-INF-*
- Capability: GOV-CAP-*
- Evidence: GOV-EVD-*
- Administration: GOV-ADM-*
- Federation: GOV-FED-*

## AC — Aether Compute (30 components)

- Control: CMP-CTL-*
- Trust: CMP-TRU-*
- Resources: CMP-RES-*
- Execution: CMP-EXE-*
- Data: CMP-DAT-*
- Evidence: CMP-EVD-*
- Economics: CMP-ECO-*

## Flow

1. Intent enters AX (COG-INT-001).
2. AG evaluates: identity, policy, information flow, capability.
3. AG issues a signed execution order (GOV-CAP-003).
4. AC admits and executes.
5. AG correlates and seals evidence.
6. AX replays if needed (COG-ASSUR-002).
