import os

path = "inference_bridge.py"
if not os.path.exists(path):
    print(f"[-] Error: {path} not found.")
    exit(1)

with open(path, "r") as f:
    code = f.read()

# Define the engineering upgrades module
hardening_code = '''

import time
from collections import deque
from fastapi import Header, Security, status

# ==========================================
# ENTERPRISE HARDENING & OBSERVABILITY LAYER
# ==========================================

class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.latencies = deque(maxlen=100)
        self.token_speeds = deque(maxlen=100)

    def record(self, latency: float, tokens_per_sec: float, success: bool):
        self.request_count += 1
        if not success:
            self.error_count += 1
        self.latencies.append(latency)
        self.token_speeds.append(tokens_per_sec)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "avg_latency_ms": sum(self.latencies) / len(self.latencies) * 1000 if self.latencies else 0,
            "avg_tokens_per_sec": sum(self.token_speeds) / len(self.token_speeds) if self.token_speeds else 0
        }

metrics = MetricsCollector()
intent_semaphore = asyncio.Semaphore(1)
is_ready = False
API_TOKEN = os.getenv("ENTERPRISE_AI_TOKEN", "enterprise-secure-local-token")

async def verify_enterprise_token(x_enterprise_token: Optional[str] = Header(None)):
    if x_enterprise_token and x_enterprise_token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid enterprise security token.")
    return True

@app.get("/healthz")
async def healthz():
    return {"status": "alive", "timestamp": time.time()}

@app.get("/readyz")
async def readyz():
    global is_ready
    if not is_ready:
        raise HTTPException(status_code=503, detail="Engine not fully initialized.")
    return {
        "status": "ready",
        "nodes": len(hypergraph.graph.nodes) if hasattr(hypergraph, "graph") else 0,
        "metrics": metrics.get_summary()
    }

@app.get("/metrics")
async def get_metrics():
    return metrics.get_summary()
'''

# Check if hardening is already present
if "class MetricsCollector" not in code:
    code += hardening_code
    print("[+] Injecting Enterprise Hardening Layer...")
else:
    print("[+] Enterprise Hardening Layer already present.")

with open(path, "w") as f:
    f.write(code)

print("[+] upgrade_engine.py completed successfully.")
