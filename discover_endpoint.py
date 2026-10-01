#!/usr/bin/env python3
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

print("[*] Inspecting FastAPI OpenAPI schema for registered routes...")
try:
    req = urllib.request.Request(f"{BASE_URL}/openapi.json")
    with urllib.request.urlopen(req, timeout=5) as response:
        spec = json.loads(response.read().decode('utf-8'))
        paths = spec.get("paths", {})
        print("\n[INFO] Discovered API Endpoints:")
        for path, methods in paths.items():
            print(f"  - {path} [{', '.join(methods.keys()).upper()}]")
        
        # Find a matching inference endpoint
        target_path = None
        for path in paths:
            if any(k in path.lower() for k in ["chat", "completion", "generate", "infer", "predict"]):
                target_path = path
                break
        
        if not target_path:
            for path in paths:
                if path not in ["/health", "/docs", "/redoc", "/openapi.json"]:
                    target_path = path
                    break
        
        if target_path:
            print(f"\n[*] Testing discovered route: {target_path}")
            payload = {
                "prompt": "Verify system operational status and respond with a concise sovereign handshake.",
                "messages": [{"role": "user", "content": "Verify system operational status."}],
                "model": "mlx-community/Qwen2.5-7B-Instruct-4bit"
            }
            req_post = urllib.request.Request(
                f"{BASE_URL}{target_path}",
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                with urllib.request.urlopen(req_post, timeout=30) as resp:
                    print(f"\n[SUCCESS] Response from {target_path}:")
                    print(resp.read().decode('utf-8'))
            except Exception as post_err:
                print(f"\n[WARN] POST to {target_path} failed: {post_err}")
        else:
            print("\n[WARN] No viable POST endpoint found.")
except Exception as e:
    print(f"[FAIL] Could not fetch OpenAPI schema: {e}")
