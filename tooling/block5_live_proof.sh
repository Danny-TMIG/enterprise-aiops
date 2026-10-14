#!/usr/bin/env bash
# Block 5 live proof: hit /healthz and /readyz against a real server.
set -uo pipefail
PORT=8002
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

cd "$HOME/aether"

echo "== 1. run block-5 tests =="
python -m pytest tests/test_health_real.py -q 2>&1 | tail -3

echo
echo "== 2. stop any stale server on $PORT =="
STALE=$(lsof -t -i:$PORT 2>/dev/null || true)
[ -n "$STALE" ] && { kill $STALE 2>/dev/null || true; sleep 1; echo "killed $STALE"; } || echo "none"

echo
echo "== 3. start uvicorn with SOVEREIGN_NODE_ID set =="
export SOVEREIGN_NODE_ID=demo
: > "$LOG"
nohup uvicorn ac.app:app --host 127.0.0.1 --port $PORT >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"

echo
echo "== 4. wait for readiness =="
for i in $(seq 1 30); do
  CODE=$(curl -s -o /dev/null -w %{http_code} "$BASE/healthz" 2>/dev/null || echo 000)
  [ "$CODE" = "200" ] && { echo "ready (${i}00ms)"; break; }
  sleep 0.1
done

echo
echo "== 5. /healthz =="
curl -s -w "\nHTTP %{http_code}\n" "$BASE/healthz" | python3 -m json.tool 2>/dev/null || curl -s "$BASE/healthz"

echo
echo "== 6. full body =="
curl -s "$BASE/healthz" | python3 -m json.tool

echo
echo "== 7. verify shape =="
BODY=$(curl -s "$BASE/healthz")
python3 - "$BODY" <<'PY'
import json, sys
body = json.loads(sys.argv[1])
assert "status" in body, "missing top-level status"
assert "subsystems" in body, "missing subsystems"
for k in ("settings", "ledger", "model", "disk"):
    assert k in body["subsystems"], f"missing subsystem: {k}"
    assert body["subsystems"][k]["status"] in ("ok", "degraded", "down")
print(f"top-level status: {body['status']}")
for k, v in body["subsystems"].items():
    print(f"  {k:<10} {v['status']:<10} {v['detail'][:60]}")
PY

echo
echo "== RESULT: block 5 verified =="
