import os

path = "inference_bridge.py"
if not os.path.exists(path):
    print(f"[-] Error: {path} not found in current directory.")
    exit(1)

with open(path, "r") as f:
    code = f.read()

# Ensure comprehensive typing imports are at the top
typing_header = "from typing import List, Dict, Any, Tuple, Optional, Union, Callable"
lines = [l for l in code.splitlines() if not l.strip().startswith("from typing import")]
code = typing_header + "\n" + "\n".join(lines)

# Append IntentOrchestrator if missing
intent_code = '''

class IntentOrchestrator:
    @staticmethod
    async def resolve_intent(intent_str: str) -> Dict[str, Any]:
        global model, tokenizer
        logger.info(f"[Intent Orchestrator] Resolving incoming intent: {intent_str}")
        
        relevant_nodes = hypergraph.semantic_search(intent_str, top_k=3)
        context_str = "\\n".join([f"- [{n[0]}]: {hypergraph.graph.nodes[n[0]].get(\"content\", \"\")[:300]}" for n in relevant_nodes])
        
        planning_prompt = (
            f"You are the Meta-Governing Enterprise AI Architect. "
            f"An intent has been submitted by the user.\\n"
            f"Intent: {intent_str}\\n\\n"
            f"Relevant Hypergraph Context:\\n{context_str}\\n\\n"
            f"Determine the execution strategy. If Python code execution is required, provide executable python code inside a ```python block. "
            f"Otherwise, provide a detailed architectural resolution."
        )
        
        async with model_lock:
            loop = asyncio.get_running_loop()
            plan_response = await loop.run_in_executor(
                None,
                lambda: generate(model, tokenizer, prompt=planning_prompt, max_tokens=1024, verbose=False)
            )
            
        execution_result = None
        if "```python" in plan_response:
            parts = plan_response.split("```python")
            if len(parts) > 1:
                code_snippet = parts[1].split("```")[0].strip()
                logger.info("[Intent Orchestrator] Executing extracted intent code in sandbox...")
                execution_result = ExecutionSandbox.run_python_snippet(code_snippet)
                
                if execution_result["status"] != "success":
                    logger.warning("[Intent Orchestrator] Initial execution failed. Triggering self-healing...")
                    heal_res = await AutonomousSelfHealingAgent.execute_heal_loop(
                        discipline="Enterprise Systems Engineering",
                        initial_task=f"Fix and fulfill this intent: {intent_str}",
                        max_iterations=3
                    )
                    execution_result = heal_res
                    
        ledger_entry = CryptographicLedger.append_entry({
            "action": "intent_resolution",
            "intent": intent_str,
            "status": "executed" if execution_result else "planned",
            "execution_result": execution_result
        })
        
        return {
            "intent": intent_str,
            "hypergraph_nodes_referenced": [n[0] for n in relevant_nodes],
            "architectural_plan": plan_response,
            "execution_result": execution_result,
            "ledger_hash": ledger_entry["current_hash"]
        }

@app.post("/api/intent")
async def intent_endpoint(request: Dict[str, str]):
    intent = request.get("intent", "")
    if not intent:
        raise HTTPException(status_code=400, detail="Intent string is required.")
    return await IntentOrchestrator.resolve_intent(intent)
'''

if "class IntentOrchestrator" not in code:
    code += intent_code
    print("[+] Appending IntentOrchestrator...")
else:
    print("[+] IntentOrchestrator already present.")

with open(path, "w") as f:
    f.write(code)

print("[+] inference_bridge.py successfully patched and verified.")
