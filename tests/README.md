# tests

Monorepo test suite. Run with pytest from repo root.

## Files

- __init__.py            marks tests as a package
- conftest.py            pytest fixtures; provides `client` (TestClient)
- test_api.py            HTTP endpoint tests
- test_engine_patch.py   engine primitive unit tests

## Run

    pytest -q
    pytest tests/test_api.py -q
    pytest -k merkle -q

## Fixtures

- client (tests/conftest.py) -> fastapi.testclient.TestClient bound to
  aiops_platform.app.asgi.app

## Coverage targets

- aiops_platform/app/api/__init__.py
- aiops_platform/app/asgi.py (route /)
- aiops_platform/app/core/engine_patch.py
- aiops_platform/app/db/__init__.py (connect creates events table)

## Test inventory

test_api.py
- test_health         GET /health status 200, status=="ok", service=="aiops_platform"
- test_version        GET /version status 200, version=="1.0.0"
- test_root           GET / status 200, merkle_root length 64, patches >= 1

test_engine_patch.py
- test_apply_and_history       empty history, one record after apply
- test_merkle_root_is_stable   same payload -> same root
- test_merkle_root_changes     different payload -> different root
