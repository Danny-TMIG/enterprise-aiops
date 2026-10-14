#!/usr/bin/env bash
# Block 4 live proof. Starts uvicorn, fires requests, scrapes /metrics, kills server.
# Writes its own intermediate files under /tmp. No heredocs, no escaped quotes.
set -uo pipefail

PORT=8001
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

cd "$HOME/aether" || { echo "no repo at $HOME/aether"; exit 1; }

echo "== 1. run pytest =="
python -m pytest tests/test_app_metrics.py -q 2>&1 | tail -3

echo
echo "== 2. stop any stale server on $PORT =="
STALE=$(lsof -t -i:$PORT 2>/dev/null || true)
if [ -n "$STALE" ]; then
  kill $STALE 2>/dev/null || true
  sleep 1
  echo "killed stale pid(s): $STALE"
else
  echo "no stale server"
fi

echo
echo "== 3. start uvicorn =="
: > "$LOG"
nohup uvicorn ac.app:app --host 127.0.0.1 --port $PORT >> "$LOG" 2>&1 &
UVPID=$!
echo "$UVPID" > "$PIDFILE"
echo "started pid $UVPID, log at $LOG"

echo
echo "== 4. wait for readiness =="
READY=0
for i in $(seq 1 30); do
  CODE=$(curl -s -o /dev/null -w %{http_code} "$BASE/healthz" 2>/dev/null || echo 000)
  if [ "$CODE" = "200" ]; then
    READY=1
    echo "ready after ${i}0ms (healthz=$CODE)"
    break
  fi
  sleep 0.1
done
if [ "$READY" != "1" ]; then
  echo "server did not become ready in 3s"
  echo "--- last 40 lines of $LOG ---"
  tail -40 "$LOG"
  exit 1
fi

echo
echo "== 5. fire requests =="
for i in 1 2 3; do
  curl -s -o /dev/null -X POST "$BASE/api/v1/execute" \
    -H 'Content-Type: application/json' \
    --data-binary '{"a":1}'
done
curl -s -o /dev/null "$BASE/does-not-exist"
echo "sent 3 POSTs + 1 404"

echo
echo "== 6. scrape /metrics =="
curl -s "$BASE/metrics" | grep sovereign_requests_total || echo "(no sovereign_requests_total lines found)"

echo
echo "== 7. verify =="
BODY=$(curl -s "$BASE/metrics")
POST_LINE=$(printf '%s\n' "$BODY" | grep 'method="POST"' || true)
GET_LINE=$(printf '%s\n' "$BODY" | grep 'method="GET"' || true)

FAIL=0
case "$POST_LINE" in
  *'path="/api/v1/execute"'*'status_class="2"}'*' 3.0'*) echo "ok  POST series = 3.0" ;;
  *) echo "FAIL POST series"; printf '  got: %s\n' "$POST_LINE"; FAIL=1 ;;
esac
case "$GET_LINE" in
  *'path="unmatched"'*'status_class="4"}'*' 1.0'*) echo "ok  GET unmatched series = 1.0" ;;
  *) echo "FAIL GET series"; printf '  got: %s\n' "$GET_LINE"; FAIL=1 ;;
esac

echo
if [ "$FAIL" = "0" ]; then
  echo "== RESULT: all checks green =="
else
  echo "== RESULT: checks failed =="
  echo "--- last 20 lines of $LOG ---"
  tail -20 "$LOG"
  exit 1
fi
