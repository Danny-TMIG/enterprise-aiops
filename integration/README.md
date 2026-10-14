# integration/

## What is here

Tests that exercise the system across component and layer boundaries.

| Path | Purpose |
|---|---|
| `cross-layer/` | Objects crossing Cognition / Govern / Compute boundaries |
| `authority/` | Identity, delegation, consent, approval, revocation |
| `sovereignty/` | Cross-domain non-leakage, federation non-transfer |
| `e2e/` | Full-stack diagnostic and end-to-end tests |

## What belongs here

Tests that verify *boundaries*, not behavior of any single component.
Component behavior is tested in `components/*/*/tests/`.

## Current state

| Directory | Status |
|---|---|
| `e2e/` | **Active.** Contains `test_full_stack_diagnostic.py`, which passes |
| `cross-layer/` | Empty |
| `authority/` | Empty |
| `sovereignty/` | Empty |

The `e2e/` diagnostic is the only integration test that currently exists.
It exercises one path from each of AC, AG, and AX end to end. The three
empty directories are where the highest-value missing tests should go.
