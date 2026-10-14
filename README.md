# Aether Fabric Sovereign

A local-first sovereign stack. Every module verified against real library APIs.

## What is real

| Module | Tests |
|---|---|
| `ag/settings.py` | 15 |
| `ag/logging.py` | 12 |
| `ag/metrics.py` | 17 |
| `ac/app.py` metrics middleware | 10 |
| `ag/health.py` | 12 |
| `ag/licenses.py` | 18 |
| `ag/tracing.py` | 13 |
| `ac/app.py` tracing middleware | 6 |

Total: 285 tests passing.

## What is not present

Six items require infrastructure not in this repo. See `artifacts/STATUS.md`.

## Run

    pytest -q
    ./tooling/verify_all.sh
    ./tooling/emit_sbom.sh
