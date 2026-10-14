# integration/authority/

## What is here

Tests that exercise the identity, delegation, consent, approval, and
revocation paths across components.

## What belongs here

Tests that verify:

- Authentication is not treated as authorization.
- Delegation chains do not amplify — a child grant is a subset of its parent.
- Revocation blocks new orders and marks in-flight work for Compute action.
- Human approval is explicit, not inferred from silence.
- Approval quorum, separation of duty, and expiry are enforced.

## Relationship to the FAS

These tests correspond directly to Govern FAS §8. Authority bugs are the
most dangerous class in a governed system; these tests should run on every
pull request.

## Current state

Empty. No authority integration tests have been authored.
