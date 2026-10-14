# integration/sovereignty/

## What is here

Tests that verify a sovereign domain does not leak private state into
another domain, and that federation does not transfer authority.

## What belongs here

Tests that verify:

- Global ASF consultation does not authorize disclosure of unrelated
  private state.
- A requesting domain independently controls outbound disclosure and
  inbound release.
- Cross-domain consultation does not transfer sovereignty.
- Caller state is not retained by the consulted domain without explicit
  authorization.

## Status

Most of this territory is **deferred** — `GOV-DEC-011` and `CMP-DEC-017`
are both Deferred. What exists here in v1 should be fixtures and
placeholders that encode the constraints any future federation
implementation must satisfy. A sovereignty test that passes when a private
state leaks is the highest-cost failure mode in the suite.

## Current state

Empty.
