#!/bin/bash
set -e
source .venv/bin/activate
echo "========================================================"
echo "=== ENTERPRISE AIOPS UNIFIED EXECUTION & WIRING MATRIX ==="
echo "========================================================"
echo "[1/4] Running Import Guard Audit..."
python scripts/import_guard.py
echo "[2/4] Executing Compilation & Build Benchmarks..."
./scripts/compile_all.sh
echo "[3/4] Executing Nested Universal Assembly Suite..."
./scripts/nested_assemble.sh
echo "[4/4] Reclaiming Port 8000 & Launching Control Plane..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
exec python -m app.__main__
