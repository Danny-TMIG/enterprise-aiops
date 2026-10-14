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
from sovereign.model import generate as model_generate


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "sovereign" / "config.json").read_text())
LEDGER = Ledger(ROOT / CONFIG["ledger_path"])
MODEL_PATH = ROOT / CONFIG["model_path"]



def _validate(req: ChatRequest) -> str | None:
    """Return error message or None if the request is valid."""
    if not req.messages:
        return "messages must not be empty"
    for i, m in enumerate(req.messages):
        if m.role not in ("user", "assistant", "system"):
            return f"messages[{i}].role must be one of user, assistant, system"
        if not isinstance(m.content, str):
            return f"messages[{i}].content must be a string"
        if not m.content.strip():
            return f"messages[{i}].content must not be empty"
    if req.max_tokens < 1 or req.max_tokens > 4096:
        return "max_tokens must be between 1 and 4096"
    if req.temperature < 0.0 or req.temperature > 2.0:
        return "temperature must be between 0.0 and 2.0"
    return None


app = FastAPI(title="Sovereign Node", version="1.0")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "tiny-local"
    messages: list[Message]
    max_tokens: int = 256
    temperature: float = 0.0


@app.get("/health")
def health() -> dict[str, Any]:
    subsystems = {}

    # config
    backend_ok = CONFIG.get("backend") in CONFIG.get("backends", {})
    subsystems["config"] = "ok" if backend_ok else "down"

    # model
    model_ok = MODEL_PATH.exists()
    subsystems["model"] = "ok" if model_ok else "degraded"

    # ledger
    try:
        ledger_ok = LEDGER.path.parent.exists()
        subsystems["ledger"] = "ok" if ledger_ok else "down"
    except Exception:
        subsystems["ledger"] = "down"

    if any(v == "down" for v in subsystems.values()):
        top = "down"
    elif any(v == "degraded" for v in subsystems.values()):
        top = "degraded"
    else:
        top = "ok"

    return {
        "status": top,
        "node_id": CONFIG["node_id"],
        "backend": CONFIG["backend"],
        "model": CONFIG["model"],
        "model_path": str(MODEL_PATH),
        "subsystems": subsystems,
    }


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> dict[str, Any]:
    err = _validate(req)
    if err:
        raise HTTPException(
            status_code=400,
            detail={"error": {"message": err, "type": "invalid_request_error"}},
        )
    t0 = time.time()
    request_id = f"chatcmpl-{uuid.uuid4()}"
    try:
        content, prompt_tokens, completion_tokens = model_generate(
            MODEL_PATH,
            [m.model_dump() for m in req.messages],
            max_tokens=req.max_tokens,
        )
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
