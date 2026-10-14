# Runbook — logistics-cell

Owner: logistics-team

## Purpose
Logistics departmental cell — compute contract kernel, execution gateway, data staging and result collection.

## Dependencies
- governance-cell

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

---

## Build status

This unit is intentionally `artifact.status = "declared-not-built"`.

Reason: its `constituent_components` reference public interfaces that do not yet
have real bodies behind them in `components/<layer>/<id>/src/public/`. Building a
wheel here would require fabricating implementations, which the ASF anti-stub
rule forbids. The unit is declared, cross-referenced, and validated; it is not
built.
