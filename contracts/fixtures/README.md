# contracts/fixtures/

## What is here

Valid and invalid instances of every boundary object, used by the contract
test suite to verify schema acceptance and rejection.

## Required coverage

Every boundary object needs at least four fixtures:

| Fixture | Purpose |
|---|---|
| Valid | Confirms the schema accepts well-formed input |
| Malformed | Confirms rejection of structurally invalid input |
| Expired | Confirms fail-closed on stale validity windows |
| Unsigned | Confirms rejection of objects missing integrity |

## Rules

- Fixtures are hand-written, small, and stable.
- No fixture contains real credentials, personal data, or anything
  sensitive.
- A fixture that passes when it should fail indicates a test bug, not a
  schema bug.

## Current state

Empty. Populate alongside `contracts/schemas/*/` as schemas are authored.
