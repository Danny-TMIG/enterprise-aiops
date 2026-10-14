# libraries/

## What is here

Shared primitives used by more than one component.

| Path | Purpose |
|---|---|
| `auth/` | Authentication and authorization primitives |
| `crypto/` | Cryptographic primitives — hashing, signing, key derivation |
| `logging/` | Structured logging and telemetry |

## Dependency direction

Components depend on libraries. Libraries must not depend on components.

## Rules

- **Narrow interface.** Each library exposes the minimum needed. A
  library that grows policy is a bug; policy belongs in a Govern
  component.
- **Strong coverage.** A bug in a library affects every component.
- **Stable API.** Changes ripple everywhere.

## Current state

| Library | Status |
|---|---|
| `crypto/` | Has `sovereign_crypto.py` |
| `auth/` | Empty |
| `logging/` | Empty |

Only `crypto/` has any content. `auth/` and `logging/` are placeholders
that need shared primitives factored out of the components.
