import os

path = "inference_bridge.py"
if not os.path.exists(path):
    print("[-] inference_bridge.py not found.")
    exit(1)

with open(path, "r") as f:
    code = f.read()

import_str = "from moa_moe import MixtureOfExpertsRouter, MixtureOfAgentsPipeline\n"
if "from moa_moe import" not in code:
    code = import_str + code

# Replace standard intent resolution with MoE/MoA pipeline integration if not already present
target_snippet = """    @staticmethod
    async def resolve_intent(intent: str) -> Dict[str, Any]:"""

if target_snippet in code and "MixtureOfExpertsRouter.route" not in code:
    # Inject MoE/MoA calls inside IntentOrchestrator.resolve_intent
    old_method_signature = "    @staticmethod\n    async def resolve_intent(intent: str) -> Dict[str, Any]:"
    replacement = """    @staticmethod
    async def resolve_intent(intent: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. MoE Routing: Deterministic expert selection
        expert_persona = MixtureOfExpertsRouter.route(intent)
        logger.info(f"[MoE Router] Intent routed to domain expert: [{expert_persona}]")

        # 2. Hypergraph Context Retrieval
        relevant_nodes = hypergraph.search_nodes(intent, top_k=5)"""
        
    code = code.replace(old_method_signature, replacement, 1)
    
    # Update return payload to include MoA synthesis
    old_return = '"architectural_plan": plan_response,'
    new_return = '"architectural_plan": plan_response,\n            "moa_synthesis": await MixtureOfAgentsPipeline.synthesize(intent, expert_persona, relevant_nodes),'
    code = code.replace(old_return, new_return, 1)

with open(path, "w") as f:
    f.write(code)

print("[+] inference_bridge.py successfully patched with MoE & MoA pipeline.")
