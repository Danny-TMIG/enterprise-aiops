# aiops_platform

Sovereign local-first AIOps platform. FastAPI ASGI application with a
SQLite event ledger and a Merkle-rooted versioned patch engine.

## Install

    pip install -r requirements.txt

## Run

    python3 -m aiops_platform.app.asgi

Uvicorn form:

    uvicorn aiops_platform.app.asgi:app --host 127.0.0.1 --port 8000

Installed console script:

    pip install -e .
    aiops-serve

## Endpoints

    GET /health    -> {"status":"ok","service":"aiops_platform"}
    GET /version   -> {"version":"1.0.0"}
    GET /          -> {"service":"aiops_platform","merkle_root":"<64 hex>","patches":N}

## Package layout

    aiops_platform/
      __init__.py          __version__ = "1.0.0"
      app/
        __init__.py        empty package marker
        asgi.py            FastAPI app, /, main(), __main__ guard
        api/
          __init__.py      APIRouter with /health and /version
        core/
          __init__.py      empty
          engine_patch.py  PatchRecord, SovereignEnginePatch
        db/
          __init__.py      connect(), DB_PATH, events table DDL

## aiops_platform/app/

ASGI layer. Owns the FastAPI instance, mounts the api router, exposes
GET / for service metadata. Reads nothing from disk at import time
except module code.

## aiops_platform/app/asgi.py

- Imports: uvicorn, fastapi.FastAPI, aiops_platform.app.api.router,
  aiops_platform.app.core.engine_patch.SovereignEnginePatch
- Module-level: app = FastAPI(...); app.include_router(router);
  _engine = SovereignEnginePatch(); _engine.apply("bootstrap", {"stage":"asgi-import"})
- Routes: GET / returns service name, merkle_root, patch count
- main(): uvicorn.run("aiops_platform.app.asgi:app", host=127.0.0.1, port=8000, reload=False)
- __main__ guard calls main()

## aiops_platform/app/api/

Pure-function route handlers. No state. No I/O. Router is mounted by asgi.py.

## aiops_platform/app/api/__init__.py

- Exports: router (fastapi.APIRouter)
- Routes:
  - GET /health -> {"status":"ok","service":"aiops_platform"}
  - GET /version -> {"version": __version__ from aiops_platform}

## aiops_platform/app/core/

Engine primitives. Currently one module: engine_patch.

## aiops_platform/app/core/engine_patch.py

- Classes:
  - PatchRecord(name, version, applied_at, payload) with digest() -> hex str
  - SovereignEnginePatch() with apply(name, payload=None) -> PatchRecord,
    history() -> list[PatchRecord], merkle_root() -> hex str
- Merkle root is SHA-256 over concatenated per-record digests in order.
- Empty history returns SHA-256 of b"empty".

## aiops_platform/app/db/

SQLite access. No ORM. Path is package-relative, not CWD-relative.

## aiops_platform/app/db/__init__.py

- DB_PATH = <package>/../aiops.db
- connect() -> sqlite3.Connection; creates events table on first call
- events table: id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, kind TEXT,
  payload TEXT, digest TEXT
- Caller owns connection lifecycle (no auto-close).

## Environment

- AIOPS_HOST (default 127.0.0.1)
- AIOPS_PORT (default 8000)
- AIOPS_LOG_LEVEL (default info)
- AIOPS_DB_PATH (default aiops.db)
See .env.example.

## Tests

    pytest -q

Covers: /health, /version, /, PatchRecord.digest stability,
SovereignEnginePatch.history, merkle_root stability and sensitivity.

## Design constraints

- Never name a package after a stdlib module.
- No import-time side effects other than _engine bootstrap patch.
- DB path resolved relative to package root, not CWD.
