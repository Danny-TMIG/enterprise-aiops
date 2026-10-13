import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from inference_bridge import InferenceStateBridge


async def main():
    bridge = InferenceStateBridge("universal_ops_ledger.jsonl")
    print("[*] Dispatching verification query to local MLX server...")
    result = await bridge.dispatch_and_prove("vatican", "Verify cryptographic state transition rules for corpus validation.")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
