#!/usr/bin/env bash
# Start the ASF web frontend.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d node_modules ]; then
  echo "[*] installing dependencies (first run)..."
  npm install
fi

echo "[*] regenerating status.json..."
cd ..
python3 tooling/validation/status_json.py
cd web

echo "[*] starting dev server on http://localhost:5173"
npm run dev
