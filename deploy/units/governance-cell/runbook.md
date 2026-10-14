# Runbook — governance-cell

Owner: govern-team

## Purpose
Enterprise governance authority — object model registry, state/transition engine, decision/outcome correlation.

## Dependencies

## Diagnostics
- `curl http://127.0.0.1:<port>/healthz`
- Inspect the unit's state directory for SQLite files.

## Containment
Stop only this unit. Never touch a peer unit's state directory.

## Backup / restore
- Backup: copy state directory to cold storage.
- Restore: stop unit, restore state directory, restart.

## Rollback
Restore the artifact digest recorded in the release manifest.

## Incident evidence
Emit to `dcs/evidence/` and `deploy/ledgers/federation_evidence.jsonl`.
