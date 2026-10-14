"""
Aether Sovereign Fabric — Master Release & Publish Automation
"""

import subprocess
import sys

def run_cmd(cmd: list[str]) -> None:
    print(f"⚙️ [EXEC] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Error executing {' '.join(cmd)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 [RELEASE] Initializing Aether Sovereign Release Pipeline...")
    run_cmd(["python3", "tooling/master_orchestrator.py"])
    run_cmd(["pytest", "-v"])
    run_cmd(["git", "add", "."])
    run_cmd(["git", "commit", "-s", "-m", "feat(sovereign): finalize all auxiliary modules, gateways, and telemetry stores"])
    print("✔ [READY] Monorepo staged and ready for remote push.")
