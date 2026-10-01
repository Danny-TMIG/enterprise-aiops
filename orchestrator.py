import asyncio
import sys
from pathlib import Path
from inference_bridge import InferenceStateBridge

DISCIPLINES = [
    "FE", "BE", "FS", "MO", "EMB", "FW", "KRN", "SYS", "DIS", "NET", 
    "DB", "DBA", "DE", "DS", "MLE", "RES", "GFX", "GAME", "SHD", "CMP", 
    "PL", "FM", "SO", "SD", "CRY", "RE", "SRE", "DO", "PLT", "CL", 
    "REL", "QA", "AUT", "HPC", "SCI", "QT", "ROB", "SIM", "CAD", "AU", 
    "VID", "TW", "DA", "SA", "HW", "NWE", "STE", "CMP2"
]

async def autonomous_loop():
    print("[*] Igniting Fully Autonomous Multi-Agent Orchestrator via Local Ollama...")
    bridge = InferenceStateBridge()
    
    goal = "Verify state transition boundaries, optimize memory locks, and eliminate scope creep."
    print(f"[*] Ingested Goal: {goal}")
    print(f"[*] Dispatching across active engineering matrix ({len(DISCIPLINES)} disciplines)...")
    
    # Run dispatch concurrently in batches or sequentially to protect unified memory bandwidth
    for disc in DISCIPLINES[:8]:  # Initializing core governance tier
        print(f"[*] Querying [{disc}] worker...")
        res = await bridge.dispatch_task(disc, goal)
        print(f"[{disc}] Status: {res['status']}")

    print("[*] Core governance pipeline cycle complete. Ledger updated.")

if __name__ == "__main__":
    asyncio.run(autonomous_loop())
