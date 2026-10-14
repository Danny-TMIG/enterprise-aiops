#!/usr/bin/env python3
"""Sovereign node — OpenAI-compatible local inference server with evidence ledger.

Runs on one machine. No cloud. Every request is written to a
tamper-evident ledger before the response is returned.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sovereign.ledger import Ledger


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "sovereign" / "config.json").read_text())
LEDGER = Ledger(ROOT / CONFIG["ledger_path"])

app = FastAPI(title="Sovereign Node", version="1.0")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "tiny-local"
    messages: list[Message]
    max_tokens: int = 128
    temperature: float = 0.0


def _count_tokens(text: str) -> int:
    # Rough estimate: 1 token ~ 4 characters. Real backends use a tokenizer.
    return max(1, len(text) // 4)


def _generate(request: ChatRequest) -> tuple[str, int, int]:
    """Deterministic placeholder that proves the pipeline.

    Replace with a real backend call (mlx_lm or transformers) when a model
    is available at config["model_path"]. The pipeline — ledger, wire format,
    hashing — is identical either way.
    """
    prompt_text = " ".join(m.content for m in request.messages)
    prompt_tokens = _count_tokens(prompt_text)
    # Echo-style response so the pipeline is observable end to end.
    response = f"[sovereign] received {len(request.messages)} message(s) for model {request.model}"
    completion_tokens = _count_tokens(response)
    return response, prompt_tokens, completion_tokens


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "node_id": CONFIG["node_id"],
        "backend": CONFIG["backend"],
        "model": CONFIG["model"],
    }


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> dict[str, Any]:
    t0 = time.time()
    request_id = f"chatcmpl-{uuid.uuid4()}"
    try:
        content, prompt_tokens, completion_tokens = _generate(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    wall_ms = (time.time() - t0) * 1000.0
    response_body = {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0,
            },
        },
        "choices": [{
            "message": {"role": "assistant", "content": content},
            "logprobs": None,
            "finish_reason": "stop",
            "index": 0,
        }],
    }

    LEDGER.append(
        request=req.model_dump(),
        response=response_body,
        meta={
            "request_id": request_id,
            "model": req.model,
            "backend": CONFIG["backend"],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "wall_ms": wall_ms,
        },
    )

    return response_body


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "sovereign.node:app",
        host=CONFIG["host"],
        port=CONFIG["port"],
        reload=False,
    )
