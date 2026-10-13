#!/usr/bin/env bash
set -e

cd ~/enterprise_aiops

# 1. Create local virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[+] Creating local virtual environment (.venv)..."
    python3 -m venv .venv
fi

# 2. Activate the virtual environment
echo "[+] Activating virtual environment..."
source .venv/bin/activate

# 3. Upgrade pip and install all required dependencies
echo "[+] Installing project dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic networkx numpy mlx mlx-lm

# 4. Clean up any conflicting local files just in case
rm -f random.py

# 5. Run the Uvicorn server
echo "[+] Launching inference bridge server..."
uvicorn inference_bridge:app --host 127.0.0.1 --port 8000 --reload
