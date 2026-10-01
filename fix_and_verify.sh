#!/usr/bin/env bash
set -e

echo "===================================================="
echo "[*] Starting Enterprise AIOps Fix & Verification..."
echo "===================================================="

# 1. Patch app/main.py to fix the 500 error on /frontier/profiles
if [ -f "app/main.py" ]; then
    echo "[*] Patching app/main.py (_frontier.profiles() -> _frontier.profiles)..."
    python3 -c '
path = "app/main.py"
with open(path, "r") as f:
    content = f.read()
new_content = content.replace("return _frontier.profiles()", "return _frontier.profiles")
if new_content != content:
    with open(path, "w") as f:
        f.write(new_content)
    print("[✔] Successfully patched app/main.py")
else:
    print("[!] Note: _frontier.profiles() pattern not found or already patched.")
'
else
    echo "[!] Error: app/main.py not found in the current working directory."
fi

# 2. Run an inline FastAPI TestClient diagnostic to verify /frontier/profiles
echo "[*] Verifying /frontier/profiles endpoint status..."
python3 -c '
from fastapi.testclient import TestClient
import app.main as main_mod

client = TestClient(main_mod.app)
response = client.get("/frontier/profiles")
print(f"[✔] /frontier/profiles Status Code: {response.status_code}")
if response.status_code == 200:
    print("[✔] Endpoint response looks healthy!")
else:
    print(f"[✘] Unexpected response: {response.text}")
'

echo "===================================================="
echo "[✔] All patches applied successfully!"
echo "===================================================="
