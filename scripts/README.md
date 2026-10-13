# scripts

Developer helpers. Not installed with the package. Run from repo root.

## Files

- __init__.py    marks scripts as a package
- smoke.py       end-to-end: start ASGI app, curl two endpoints, exit

## Run

    python3 scripts/smoke.py

## smoke.py

- Spawns `python3 -m aiops_platform.app.asgi` via subprocess.Popen
- Waits 2s for bind
- GETs http://127.0.0.1:8000/health and http://127.0.0.1:8000/
- Prints responses
- Terminates server in finally block; waits up to 5s
- Returns 0 on success, raises on failure
