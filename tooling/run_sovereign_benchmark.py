"""
Sovereign MLX & Routing Node Benchmark Suite with WORM Ledger Logging
The Mark Intelligence Group - Universal Construction System (UCS)
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
import httpx

# Ensure monorepo root is in path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ag.ledger import Ledger

TARGET_ENDPOINTS = [
    {"name": "tiny-local-mlx", "url": "http://127.0.0.1:8080/v1/chat/completions"},
    {"name": "aether-core-asgi", "url": "http://127.0.0.1:8000/api/v1/execute"}
]

def run_benchmarks():
    print("=========================================================================")
    print("  THE MARK INTELLIGENCE GROUP — SOVEREIGN BENCHMARK & WORM SUITE")
    print("=========================================================================")

    ledger_path = ROOT / "sovereign" / "ledger.jsonl"
    ledger = Ledger(ledger_path)

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    benchmark_results = []

    for endpoint in TARGET_ENDPOINTS:
        name = endpoint["name"]
        url = endpoint["url"]
        print(f"\n[*] Probing endpoint: {name} ({url}) ...")

        start_time = time.time()
        status_code = 0
        error_msg = None

        try:
            if "completions" in url:
                payload = {
                    "model": "tiny-local",
                    "messages": [{"role": "user", "content": "Benchmark pulse check."}],
                    "max_tokens": 16
                }
                res = httpx.post(url, json=payload, timeout=5.0)
            else:
                payload = {
                    "component_id": "BENCH-001",
                    "payload": {"probe": True},
                    "principal": "SYSTEM_BENCHMARKER"
                }
                res = httpx.post(url, json=payload, timeout=5.0)

            status_code = res.status_code
            if status_code != 200:
                error_msg = f"HTTP {status_code}: {res.text}"
        except Exception as e:
            error_msg = str(e)
            status_code = 503

        duration_ms = (time.time() - start_time) * 1000.0

        result_entry = {
            "node": name,
            "url": url,
            "status_code": status_code,
            "latency_ms": round(duration_ms, 2),
            "healthy": status_code == 200,
            "error": error_msg
        }
        benchmark_results.append(result_entry)
        print(f"    -> Status: {status_code} | Latency: {duration_ms:.2f}ms")

    # Construct ledger audit record
    audit_payload = {
        "benchmark_suite": "Aether Sovereign Multi-Node Probe",
        "timestamp": timestamp,
        "hardware_target": "Apple M4 Max (16 Cores, 128GB RAM)",
        "results": benchmark_results
    }

    audit_receipt = {
        "verified": all(r["healthy"] for r in benchmark_results),
        "total_nodes_tested": len(benchmark_results)
    }

    # Append to WORM ledger with fsync serialization
    ledger.append(audit_payload, audit_receipt, {"request_id": f"bench-{int(time.time())}"})
    print(f"\n[SUCCESS] Benchmark execution logged to WORM ledger: {ledger_path}")

    # Verify ledger integrity immediately
    checked, valid, errors = ledger.verify()
    print(f"    • Ledger Integrity Check: Checked={checked}, Valid={valid}, Errors={len(errors)}")

if __name__ == "__main__":
    run_benchmarks()
