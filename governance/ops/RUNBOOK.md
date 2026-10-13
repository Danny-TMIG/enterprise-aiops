# Operations Runbook

Generated: 2026-10-01T17:52:03.353255+00:00
Commit: 719c9811dd8132d32191c24d7246e51120b2aa92

## Deploy
pip install dist/dcs-0.5.0-py3-none-any.whl

## Verify
python -c "from dcs.self import MANIFESTS; print(len(MANIFESTS))"

## Rollback
pip install dcs==<previous>

## Incident
1. Freeze CT log
2. Rotate key
3. Republish manifest
4. Notify
