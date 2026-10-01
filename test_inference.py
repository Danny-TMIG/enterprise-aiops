#!/usr/bin/env python3
import urllib.request
import json
import sys

url = "http://127.0.0.1:8000/v1/chat/completions"
payload = {
    "model": "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "messages": [
        {"role": "user", "content": "Verify system operational status and respond with a concise sovereign handshake."}
    ],
    "max_tokens": 100
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    print("[*] Sending test inference request to local model server...")
    with urllib.request.urlopen(req, timeout=30) as response:
        body = json.loads(response.read().decode('utf-8'))
        print("\n[SUCCESS] Response received:")
        print(json.dumps(body, indent=2))
except Exception as e:
    print(f"\n[FAIL] Inference request failed: {e}")
    sys.exit(1)
