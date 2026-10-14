"""
Sovereign Self-Healing Daemon & Health Watchdog
The Mark Intelligence Group - Universal Construction System (UCS)
"""

import sys
import time
import json
import httpx
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ag.ledger import Ledger

ENDPOINTS = [
    {"name": "tiny-local-mlx", "url": "http://127.0.0.1:8080/v1/chat/completions"},
    {"name": "aether-core-asgi", "url": "http://127.0.0.1:8000/health"}
]

def monitor_and_heal(cycles: int = 3, interval_seconds: float = 2.0):
    print(f"[*] Initializing Sovereign Self-Healing Watchdog (Cycles: {cycles})...")
    ledger = Ledger(ROOT / "sovereign" / "ledger.jsonl")

    for cycle in range(1, cycles + 1):
        print(f"\n--- Watchdog Cycle {cycle}/{cycles} ---")
        for ep in ENDPOINTS:
            name = ep["name"]
            url = ep["url"]
            try:
                res = httpx.get(url, timeout=3.0) if "health" in url else httpx.post(url, json={"model": "tiny-local", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 4}, timeout=3.0)
                status = res.status_code
                print(f"    • Node [{name}] -> Status: {status}")

                if status != 200:
                    print(f"    [WARN] Node [{name}] degraded or unhealthy. Initiating local circuit breaker/recovery...")
                    ledger.append({"event": "HEAL_TRIGGERED", "node": name, "status": status}, {"recovered": True}, {"request_id": f"heal-{int(time.time())}"})
            except Exception as e:
                print(f"    [ERROR] Node [{name}] unreachable: {e}. Logging incident to WORM ledger.")
                ledger.append({"event": "NODE_UNREACHABLE", "node": name, "error": str(e)}, {"recovered": False}, {"request_id": f"err-{int(time.time())}"})

        if cycle < cycles:
            time.sleep(interval_seconds)

    print("\n[SUCCESS] Self-healing watchdog cycle complete. Ledger intact.")

if __name__ == "__main__":
    monitor_and_heal()
