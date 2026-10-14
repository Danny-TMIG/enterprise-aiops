# tooling/

## What is here

Scripts that operate on the repository.

| Path | Purpose |
|---|---|
| `bootstrap/` | Stand up a dev environment or deployment from a clean checkout |
| `validation/` | Gates — status, spec audit, platform, profiles, federation |
| `release/` | Build release manifests, tag, publish |

## Rules

- **Read-only where possible.** Validation tools never mutate the repo.
  Bootstrap tools write only their declared outputs.
- **Idempotent.** Re-running produces the same result.
- **Clear success or failure.** Every script prints what it did and exits
  non-zero on failure.
- **No policy.** Tooling gates checks; it does not decide what checks
  should exist. That comes from the FAS and from `Makefile` targets.
