# Runbook — finance-cell

Owner: finance-team

## Purpose
Finance departmental cell — compute contract kernel, execution gateway, admission/quota/lease manager.

## Dependencies
["governance-cell"]

## Diagnostics
- `curl http://127.0.0.1:<port>/healthz`
- Check `state_dir` for SQLite files.

## Containment
Isolate the unit by stopping its process; do not touch peer units' state dirs.

## Backup / restore
- Backup: copy `state_dir` to cold storage.
- Restore: stop unit, restore `state_dir`, restart.

## Rollback
Restore previous artifact digest recorded in the release manifest.

## Incident evidence
Emit to `dcs/evidence/` and `deploy/ledgers/federation_evidence.jsonl`.
