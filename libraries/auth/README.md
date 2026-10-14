# libraries/auth/

## What is here

Shared authentication and authorization primitives.

## What belongs here — and what does not

**Belongs here:** the mechanics of verifying a token, checking a signature,
or resolving a principal reference.

**Does not belong here:** whether a given principal may do a given thing.
Authority decisions belong in Govern components (`GOV-IAM-*`), where they
are traceable.

## Dependency direction

Components depend on this library. This library must not depend on any
component.

## Rules

- Narrow interface: verify, resolve, sign — nothing more.
- No policy. If a function here starts encoding policy, it moves to
  `GOV-IAM-003` or `GOV-POL-002`.
- Strong test coverage. A bug here affects every component.

## Current state

Empty. No shared auth primitives have been factored out yet.
