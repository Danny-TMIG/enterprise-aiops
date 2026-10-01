
import threading
import uvicorn
import time
from app.main import app

def start_test_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

server_thread = threading.Thread(target=start_test_server, daemon=True)
server_thread.start()
time.sleep(2)  # Allow server to bind port 8000

import urllib.request
import urllib.parse
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

tests = [
    {"name": "Health Check", "method": "GET", "path": "/health"},
    {"name": "OpenAPI Spec", "method": "GET", "path": "/openapi.json"},
    {"name": "Cluster Mesh Status", "method": "GET", "path": "/cluster/status"},
    {"name": "Cluster Dispatch", "method": "POST", "path": "/cluster/dispatch?task_name=sync_weights&payload_data=active"},
    {"name": "Analyze Telemetry", "method": "POST", "path": "/analyze/telemetry", "json": [0.1, 0.5, 0.9]},
    {"name": "Vector Embedding", "method": "POST", "path": "/embed?text=enterprise_aiops_latent_space"},
    {"name": "Provenance Signing", "method": "POST", "path": "/provenance/sign?artifact_id=omega-v1&payload_summary=verified_tensor"},
    {"name": "Analytics Ledger Log", "method": "POST", "path": "/analytics/log?event_type=audit&artifact_id=omega-v1&details=clean"},
    {"name": "TLA+ Formal Verification", "method": "GET", "path": "/verify/tla"},
    {"name": "Root Status", "method": "GET", "path": "/"},
    {"name": "Models List", "method": "GET", "path": "/v1/models"},
    {"name": "Chat Completion", "method": "POST", "path": "/v1/chat/completions", "json": {"model": "qwen2.5", "messages": [{"role": "user", "content": "ping"}]}, "timeout": 10},
    {"name": "Persona Synthesis", "method": "POST", "path": "/persona/synthesize", "json": {"prompt": "status"}},
    {"name": "Autonomy Status", "method": "GET", "path": "/autonomy/status"},
    {"name": "Autonomy Step", "method": "POST", "path": "/autonomy/step", "json": {}},
    {"name": "Autonomy Decisions", "method": "GET", "path": "/autonomy/decisions"},
    {"name": "Autonomy Heals", "method": "GET", "path": "/autonomy/heals"},
    {"name": "Mesh Status", "method": "GET", "path": "/mesh/status"},
    {"name": "Mesh Rebuild", "method": "POST", "path": "/mesh/rebuild", "json": {}},
    {"name": "Mesh Nodes", "method": "GET", "path": "/mesh/nodes"},
    {"name": "Mesh Graph", "method": "GET", "path": "/mesh/graph"},
    {"name": "Mesh Route", "method": "POST", "path": "/mesh/route", "json": {"source": "node-1", "destination": "node-2", "payload": {}}},
    {"name": "Mesh Planes", "method": "GET", "path": "/mesh/planes"},
    {"name": "Topos Status", "method": "GET", "path": "/topos/status"},
    {"name": "Topos Objects", "method": "GET", "path": "/topos/objects"},
    {"name": "Topos Morphisms", "method": "GET", "path": "/topos/morphisms"},
    {"name": "Topos Record", "method": "POST", "path": "/topos/record", "json": {"object_id": "obj-1"}},
    {"name": "Seed Status", "method": "GET", "path": "/seed/status"},
    {"name": "Seed Manifest", "method": "GET", "path": "/seed/manifest"},
    {"name": "Seed Intent", "method": "POST", "path": "/seed/intent", "json": {"intent": "deploy"}},
    {"name": "Seed Runs", "method": "GET", "path": "/seed/runs"},
    {"name": "Unified Status", "method": "GET", "path": "/status/unified"},
    {"name": "Moat Status", "method": "GET", "path": "/moat/status"},
    {"name": "Moat Score", "method": "GET", "path": "/moat/score"},
    {"name": "Moat Mesh", "method": "GET", "path": "/moat/mesh"},
    {"name": "Moat Refresh", "method": "POST", "path": "/moat/refresh", "json": {}},
    {"name": "Reality Status", "method": "GET", "path": "/reality/status"},
    {"name": "Reality Install", "method": "GET", "path": "/reality/install"},
    {"name": "Proprietary Status", "method": "GET", "path": "/proprietary/status"},
    {"name": "Frontier Status", "method": "GET", "path": "/frontier/status"},
    {"name": "Frontier Profiles", "method": "GET", "path": "/frontier/profiles"},
    {"name": "Frontier Invoke", "method": "POST", "path": "/frontier/invoke", "json": {"profile": "default", "prompt": "test"}},
]

def run_e2e_tests():
    print("==================================================")
    print("  Omni-NCF Fabric: Full End-to-End Test Suite")
    print("==================================================")
    
    passed = 0
    failed = 0

    for test in tests:
        url = BASE_URL + test["path"]
        method = test["method"]
        timeout = test.get("timeout", 5)
        data = json.dumps(test["json"]).encode("utf-8") if "json" in test else None
        headers = {"Content-Type": "application/json"} if data else {}

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
                if status in [200, 201]:
                    print(f"[✔] SUCCESS: {test['name']} ({method} {test['path']}) -> Status {status}")
                    passed += 1
                else:
                    print(f"[✘] FAILED:  {test['name']} ({method} {test['path']}) -> Status {status}")
                    failed += 1
        except urllib.error.HTTPError as e:
            print(f"[✘] FAILED:  {test['name']} ({method} {test['path']}) -> Status {e.code}")
            failed += 1
        except urllib.error.URLError as e:
            print(f"[!] ERROR:   {test['name']} ({method} {test['path']}) -> Unreachable: {e.reason}")
            failed += 1
        except Exception as e:
            print(f"[!] ERROR:   {test['name']} ({method} {test['path']}) -> {e}")
            failed += 1

    print("==================================================")
    print(f"Test Summary: {passed} Passed, {failed} Failed")
    print("==================================================")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_e2e_tests()
