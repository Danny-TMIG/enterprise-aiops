# integration/cross-layer/

## What is here

Tests that exercise objects crossing a boundary between Cognition, Govern,
and Compute.

## What belongs here

Tests that verify:

- Every boundary object carries a valid Common Envelope.
- Idempotency keys prevent duplicate effects on retry.
- Fail-closed behavior triggers on invalid, expired, or unsigned objects.
- Cancellation and revocation propagate as observable state transitions.
- Producer-owns-validity holds: emitters sign, consumers verify.

## Runnable without external services

Where possible, tests here use fixtures from `contracts/fixtures/` and run
in-process. Boundary regressions are the most costly kind in a three-layer
system, so these tests should be fast enough to run on every PR.

## Current state

Empty. This is the highest-value test directory in the repo. Filling it
would materially raise the quality of the codebase.
