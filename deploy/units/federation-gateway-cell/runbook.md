# Runbook — federation-gateway-cell

Owner: govern-team

## Purpose

Enterprise federation gateway. Mediates all cross-domain exchange between
Operations, Finance and Logistics under a single enterprise authority.
Deny-by-default; every cross-domain flow must be authorized by a
representation request + information-flow decision + (for regulated flows)
human approval.

## Dependencies

- governance-cell

## Diagnostics

- `curl http://127.0.0.1:8090/healthz`
- `curl http://127.0.0.1:8090/flow/operations/logistics` — expect `200`
- `curl http://127.0.0.1:8090/flow/finance/operations` — expect `403`
- Check `state_dir` for the gateway SQLite file.

## Containment

Stop the gateway process only. Peers keep running; cross-domain exchange
halts (deny-by-default) but does not corrupt departmental state.

## Backup / restore

- Backup: copy `state_dir` to cold storage.
- Restore: stop gateway, restore `state_dir`, restart.

## Rollback

Restore the previous artifact digest recorded in the release manifest.
Active leases are not re-established automatically; they must be re-requested.

## Incident evidence

Emit to `dcs/evidence/` and `deploy/ledgers/federation_evidence.jsonl`.
