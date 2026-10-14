#!/usr/bin/env python3
"""
Sovereign Watchdog Telemetry & Governance Daemon
Continuously runs cross-layer diagnostics and commits cryptographic evidence seals.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))


def load_module(name, path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Load layer modules
TelemetryCollector = load_module(
    "ac_tel", root / "components/ac/CMP-EVD-001-observation-and-telemetry/src/public/telemetry.py"
).TelemetryCollector
StateTransitionEngine = load_module(
    "ag_eng",
    root / "components/ag/GOV-KRN-002-governed-state-and-transition-engine/src/public/engine.py",
).StateTransitionEngine
CognitiveRuntime = load_module(
    "ax_run", root / "components/ax/COG-CORE-001-cognitive-runtime/src/public/runtime.py"
).CognitiveRuntime


def run_watchdog_cycle(cycle_id: int):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"\n⚡ [WATCHDOG] Executing Cycle #{cycle_id} at {timestamp}")

    # 1. AC Telemetry
    collector = TelemetryCollector()
    metrics = collector.collect_metrics()

    # 2. AG State Transition
    engine = StateTransitionEngine()
    txn = engine.transition(
        object_id=f"GOV-DAEMON-CYCLE-{cycle_id}",
        from_state="MONITORING",
        to_state="EVALUATED",
        actor="watchdog-daemon",
    )

    # 3. AX Cognitive Analysis
    runtime = CognitiveRuntime()
    cpu_load = metrics["metrics"]["cpu_load_percent"]
    analysis = runtime.execute_prompt(f"Watchdog telemetry check - CPU load: {cpu_load}%")

    # 4. Seal Cryptographic Receipt
    receipt = {
        "cycle": cycle_id,
        "timestamp": timestamp,
        "metrics": metrics,
        "governance_txn": txn,
        "cognitive_output": analysis,
    }

    receipt_hash = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode("utf-8")).hexdigest()
    receipt["omega_seal"] = receipt_hash

    receipts_dir = root / "deploy" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    receipt_file = receipts_dir / f"receipt_{cycle_id:04d}.json"
    receipt_file.write_text(json.dumps(receipt, indent=2))
    print(f"  ✔ [SEAL] Omega cryptographic receipt committed: {receipt_hash[:16]}...")


def main():
    print("🛡️ [DAEMON] Starting Aether Sovereign Watchdog...")
    cycle = 1
    try:
        while True:
            run_watchdog_cycle(cycle)
            cycle += 1
            time.sleep(10)  # Run every 10 seconds
    except KeyboardInterrupt:
        print("\n🛑 [DAEMON] Watchdog shutdown requested by operator.")


if __name__ == "__main__":
    main()
