# contracts/

## What is here

The boundary between layers. Everything that crosses a boundary — schemas,
APIs, events, fixtures — lives here.

| Path | Purpose |
|---|---|
| `canonical/` | Canonical ASF schemas — the normative source of truth |
| `schemas/ax/` | Cognition-layer schema projections |
| `schemas/ag/` | Govern-layer schema projections |
| `schemas/ac/` | Compute-layer schema projections |
| `apis/` | Interface definitions |
| `events/` | Asynchronous event definitions |
| `fixtures/` | Valid and invalid instances for contract testing |

## Precedence

Canonical schemas take precedence over local names whenever an object
crosses a layer boundary. Internal projections may add implementation
detail but may not expand authority, weaken classification, remove
evidence obligations, or alter failure semantics.

## Rules

A change to anything in this directory has cross-layer effect and requires
independent review. The producer owns semantic validity at emission; the
consumer independently validates before acting.
