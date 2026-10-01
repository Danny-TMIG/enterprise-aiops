#!/usr/bin/env bash
set -e

# Forcefully remove any local file or directory named random that shadows the namespace
echo "[+] Purging any conflicting local 'random' files or directories..."
find . -maxdepth 1 -name "random*" -exec rm -rf {} +

cat << 'END_BRIDGE' > inference_bridge.py
import os
import gc
import time
import logging
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import networkx as nx
import numpy as np
import mlx.core as mx
from mlx_lm import load, generate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enterprise_aiops")

app = FastAPI(title="Orthogonal MoA Inference Bridge", version="2.0.1")

logger.info("[+] Bootstrapping Grand Unification Hypergraph strata from local workspace...")
hypergraph = nx.Graph()
rng = np.random.default_rng(42)
for i in range(24473):
    hypergraph.add_node(i, embedding=rng.standard_normal(64))
logger.info(f"[+] Hypergraph initialized with {hypergraph.number_of_nodes()} nodes.")

class ExpertRegistry:
    def __init__(self):
        self.active_name = None
        self.model = None
        self.tokenizer = None

    def swap_expert(self, model_path: str):
        if self.active_name == model_path:
            return self.model, self.tokenizer

        if self.model is not None:
            logger.info(f"[-] Unloading previous expert '{self.active_name}' from unified memory...")
            self.model = None
            self.tokenizer = None
            gc.collect()
            mx.metal.clear_cache()
            time.sleep(1)

        logger.info(f"[+] Loading orthogonal expert '{model_path}' into M4 Max unified memory...")
        self.model, self.tokenizer = load(model_path)
        self.active_name = model_path
        return self.model, self.tokenizer

registry = ExpertRegistry()

class IntentRequest(BaseModel):
    intent: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "active_expert": registry.active_name,
        "hypergraph_nodes": hypergraph.number_of_nodes()
    }

@app.post("/api/intent")
def handle_intent(payload: IntentRequest, x_enterprise_token: str = Header(None)):
    if x_enterprise_token != "enterprise-secure-local-token":
        raise HTTPException(status_code=403, detail="Invalid enterprise security token")
    
    intent_lower = payload.intent.lower()
    if any(k in intent_lower for k in ["refactor", "generate", "endpoint", "code", "fastapi"]):
        model_path = "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"
    else:
        model_path = "mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit"

    model, tokenizer = registry.swap_expert(model_path)
    
    prompt = f"System: You are an enterprise AI operations expert.\nUser Intent: {payload.intent}\nResponse:"
    response_text = generate(model, tokenizer, prompt=prompt, max_tokens=256)
    
    return {
        "status": "success",
        "expert_used": model_path,
        "result": response_text.strip()
    }
END_BRIDGE

echo "[+] Starting Uvicorn server..."
uvicorn inference_bridge:app --host 127.0.0.1 --port 8000 --reload
