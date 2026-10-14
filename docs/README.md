# docs/

## What is here

Human-readable documentation that is not per-component.

| Path | Purpose |
|---|---|
| `AUTHORITY.md` | The authority model: who can decide what |
| `STATUS.md` | Current state of the repo |
| `architecture/` | Architecture documentation, generated and hand-written |
| `decisions/` | Architecture Decision Records (ADRs) |

## What belongs here vs. elsewhere

- **Per-component docs** belong in `components/*/*/docs/`.
- **Boundary and contract docs** belong in `contracts/`.
- **Deployment docs** belong in `deploy/`.
- **Everything else human-readable** belongs here.

## Normative vs. descriptive

The FAS documents are normative. Documentation in this directory is
descriptive of the current implementation. Where they disagree, the FAS is
authoritative and this directory should note the discrepancy.
