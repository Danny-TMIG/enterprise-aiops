# contracts/canonical/

## What is here

Canonical ASF schemas — the normative source of truth for boundary object
shape.

## The boundary contract set

The objects defined here are the only legal cross-layer contracts:

| Boundary | Objects |
|---|---|
| Authority | `AuthorizationRequest`, `AuthorizationDecision` |
| Information | `InformationFlowRequest`, `InformationFlowDecision`, `GovernedKnowledgeResult` |
| Capabilities | `CapabilityRequest`, `GovernedCapabilitySet` |
| Execution | `ExecutionOrder`, `ExecutionStatus`, `ExecutionResult`, `ExecutionEvidence` |
| Closure | `GovernedOutcome`, `CognitiveStateUpdateDirective` |
| Control | `ApprovalRequest`, `CancellationRevocationDirective`, `ASFError` |
| Envelope | `CommonEnvelope` |

## Rules

- No competing authority objects. If a boundary object is not listed in the
  FAS Boundary Contract Alignment section, it does not exist.
- Every object carries the Common Envelope: schema version, object identity,
  correlation, causation, sovereign-domain, purpose, classification,
  integrity, evidence context.
- Every retry uses a stable idempotency key.
- Expired, revoked, malformed, unsupported, unsigned, or context-inconsistent
  objects fail closed.

## Relationship to other schema directories

`contracts/schemas/ax/`, `ag/`, and `ac/` hold layer-local projections that
conform to these canonical definitions. `40_CROSS_STACK_INTEGRATION/05_Canonical_Schemas/`
holds a mirror of this set for the integrated stack. Keep them in sync.
