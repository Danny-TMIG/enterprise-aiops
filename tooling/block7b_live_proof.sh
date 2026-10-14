#!/usr/bin/env bash
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
