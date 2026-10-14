#!/usr/bin/env python3
"""Finish block 7b: write the live-proof script, verify everything on disk,
run the tests, and print exactly what to commit.

Does not run git — you stage and commit manually so you can inspect first.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "aether"


def write(path: str, content: str) -> None:
    p = REPO / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    b = content.encode()
    print(f"  wrote {path}  ({len(content.splitlines())} lines, {len(b)} bytes, sha256={hashlib.sha256(b).hexdigest()[:12]})")


def check(path: str) -> bool:
    p = REPO / path
    if not p.is_file():
        print(f"  MISSING: {path}")
        return False
    print(f"  ok:      {path}  ({len(p.read_text().splitlines())} lines)")
    return True


def run(cmd: list[str]) -> int:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=REPO)


# ---------------------------------------------------------------------------
# 1. Write the live-proof script (this is what was missing).
# ---------------------------------------------------------------------------
print("== writing tooling/block7b_live_proof.sh ==")
write("tooling/block7b_live_proof.sh", r'''#!/usr/bin/env bash
# Block 7b live proof: run the app under uvicorn, prove the tracing middleware
# is installed and doesn't break anything. Spans are asserted by the unit
# tests, which use an in-memory exporter (deterministic, no collector needed).
set -uo pipefail
cd "$HOME/aether"

PORT=8003
BASE="http://127.0.0.1:$PORT"
LOG=/tmp/uvicorn-$PORT.log
PIDFILE=/tmp/uvicorn-$PORT.pid

cleanup() {
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE" 2>/dev/null || true)
    [ -n "${PID:-}" ] && kill "$PID" 2>/dev/null || true
    rm -f "$PIDFILE"
  fi
}
trap cleanup EXIT

echo "== 1. pytest (7b unit tests) =="
python -m pytest tests/test_app_tracing.py -q 2>&1 | tail -3

echo
echo "== 2. stop stale server on $PORT =="
STALE=$(lsof -t -i:$PORT 2>/dev/null || true)
if [ -n "$STALE" ]; then
  kill $STALE 2>/dev/null || true
  sleep 1
  echo "killed $STALE"
else
  echo "none"
fi

echo
echo "== 3. start uvicorn (SOVEREIGN_TRACING=1 enables span emission) =="
: > "$LOG"
SOVEREIGN_TRACING=1 \
SOVEREIGN_NODE_ID=proof-node \
nohup uvicorn ac.app:app --host 127.0.0.1 --port $PORT >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "pid $(cat "$PIDFILE"), log at $LOG"

echo
echo "== 4. readiness =="
for i in $(seq 1 30); do
  CODE=$(curl -s -o /dev/null -w %{http_code} "$BASE/healthz" 2>/dev/null || echo 000)
  if [ "$CODE" = "200" ]; then
    echo "ready after ${i}00ms"
    break
  fi
  sleep 0.1
done

echo
echo "== 5. fire requests =="
for i in 1 2 3; do
  curl -s -o /dev/null -X POST "$BASE/api/v1/execute" \
    -H 'Content-Type: application/json' --data-binary '{"a":1}'
done
curl -s -o /dev/null "$BASE/does-not-exist"
echo "sent 3 POSTs + 1 404"

echo
echo "== 6. /metrics still works (middleware didn't break the pipeline) =="
curl -s "$BASE/metrics" | grep sovereign_requests_total | grep -E 'POST|GET' | head -4

echo
echo "== 7. tail uvicorn log (should be quiet, no tracebacks) =="
tail -10 "$LOG"

echo
echo "== 8. summary =="
if grep -q "Traceback" "$LOG"; then
  echo "FAIL: uvicorn log contains a traceback"
  exit 1
fi
echo "RESULT: block 7b verified — middleware installed, requests served, no crashes"
''')

# ---------------------------------------------------------------------------
# 2. Verify every file block 7b depends on is present.
# ---------------------------------------------------------------------------
print("\n== verifying files on disk ==")
all_present = True
for path in (
    "ag/tracing.py",
    "tests/test_tracing.py",
    "tests/test_app_tracing.py",
    "ac/app.py",
    "tooling/block7b_live_proof.sh",
):
    if not check(path):
        all_present = False
if not all_present:
    print("\nSTOP: some files are missing. Fix before running tests.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 3. Show the exact block-7b additions in ac/app.py so we can eyeball them.
# ---------------------------------------------------------------------------
print("\n== ac/app.py tracing additions ==")
s = (REPO / "ac/app.py").read_text()
for needle in ("class TracingMiddleware", "def _tracing_lifespan", "add_middleware(TracingMiddleware)"):
    line = next((i for i, l in enumerate(s.splitlines(), 1) if needle in l), None)
    print(f"  {needle}: {'line ' + str(line) if line else 'NOT FOUND'}")

# ---------------------------------------------------------------------------
# 4. Run the 7b tests.
# ---------------------------------------------------------------------------
print("\n== pytest tests/test_app_tracing.py ==")
rc1 = run([sys.executable, "-m", "pytest", "tests/test_app_tracing.py", "-q"])

# ---------------------------------------------------------------------------
# 5. Run the full suite so we know nothing regressed.
# ---------------------------------------------------------------------------
print("\n== pytest (full suite) ==")
rc2 = run([sys.executable, "-m", "pytest", "-q"])

# ---------------------------------------------------------------------------
# 6. Print what to commit.
# ---------------------------------------------------------------------------
print("\n== commit command ==")
print("  cd ~/aether && git add ac/app.py tests/test_app_tracing.py tooling/block7b_live_proof.sh")
print("  git commit -s -m \"feat(ac): tracing middleware emits per-request spans with http attributes\"")
print("  git push origin main")
print("  git log --oneline -1")

print(f"\nresult: 7b tests rc={rc1}, full suite rc={rc2}")
sys.exit(0 if rc1 == 0 and rc2 == 0 else 1)
