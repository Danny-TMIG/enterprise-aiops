# Layer: ac

Directory: `ac`

## Files

    ac/__init__.py
    ac/app.py
    ac/router.py

## Contents

### `ac/__init__.py`

```
```
### `ac/app.py`

```
from fastapi import FastAPI
from ax.sovereign_client import AetherSovereignClient

app = FastAPI()
sovereign_client = AetherSovereignClient()

@app.post("/api/v1/execute")
async def execute_task(payload: dict):
    prompt = payload.get("prompt", "Generate status report for local sovereign node.")
    temperature = payload.get("temperature", 0.2)

    try:
        result = sovereign_client.query(prompt, temperature=temperature)
        ai_response = result["choices"][0]["message"]["content"]
    except Exception as e:
        ai_response = f"[ERROR] Local inference failed: {str(e)}"

    return {
        "status": "success",
        "node": "aether-core-asgi",
        "acceleration_layer": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "response": ai_response
    }
```
### `ac/router.py`

```
"""Route a control-plane decision to a sovereign node."""
from __future__ import annotations
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RouteResult:
    node_url: str
    response: dict[str, Any]
    status: int


def route(decision: dict[str, Any], nodes_config: Path) -> RouteResult:
    """Given a routing-handle decision, POST to the named node."""
    nodes = json.loads(nodes_config.read_text())
    target = decision.get("target", "default")
    node = nodes.get(target) or nodes.get("default")
    if node is None:
        raise RuntimeError(f"no node registered for target {target!r}")

    url = f"{node['url']}/v1/chat/completions"
    payload = json.dumps({
        "model": decision.get("model", "tiny-local"),
        "messages": decision.get("messages", [{"role": "user", "content": "hello"}]),
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            return RouteResult(node_url=url, response=body, status=resp.status)
    except Exception as e:
        return RouteResult(node_url=url, response={"error": str(e)}, status=0)
```
