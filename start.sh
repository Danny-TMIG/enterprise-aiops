#!/usr/bin/env bash
set -e

FORGE_HOME="${HOME}/forge"
AIOPS_HOME="${HOME}/enterprise_aiops"
PID_DIR="${AIOPS_HOME}/pids"
LOG_DIR="${AIOPS_HOME}/logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

echo "==> cleaning prior enterprise_aiops processes"
if [ -f "$PID_DIR/worker-agent.pid" ]; then
    kill $(cat "$PID_DIR/worker-agent.pid") 2>/dev/null || true
    rm -f "$PID_DIR/worker-agent.pid"
fi

echo "==> starting enterprise_aiops worker agent daemon"
cd "$AIOPS_HOME"
source "$FORGE_HOME/.venv/bin/activate"

export FORGE_NODE_ID="worker-m4-max-01"
export FORGE_CONTROL_PLANE="http://127.0.0.1:8000"
export PYTHONPATH="$AIOPS_HOME"

nohup uvicorn worker.agent:app --host 127.0.0.1 --port 8084 --log-level info > "$LOG_DIR/uvicorn.log" 2>&1 &
echo $! > "$PID_DIR/worker-agent.pid"

echo "ok enterprise_aiops worker agent running on port 8084 (pid $(cat "$PID_DIR/worker-agent.pid"))"
