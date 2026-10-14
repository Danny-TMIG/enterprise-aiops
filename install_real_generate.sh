#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

python3 - <<'PYEOF'
from pathlib import Path

# ============================================================== 1. REAL _generate
# Replace the placeholder with a model-backed implementation.
# mlx_lm is lazy-imported so the node starts even without a model present.

Path("sovereign/model.py").write_text('''"""Model backend for the sovereign node.

Lazy-loaded. If a model path exists and mlx_lm is installed, the node
serves a real model. If not, it falls back to a deterministic echo so
the pipeline (ledger, wire format, hashing) still runs end to end.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_CACHE: dict[str, Any] = {}


def _load(model_path: Path):
    """Load once, cache forever. Raise if unavailable."""
    key = str(model_path)
    if key in _CACHE:
        return _CACHE[key]

    from mlx_lm import load
    model, tokenizer = load(str(model_path))
    _CACHE[key] = (model, tokenizer)
    return _CACHE[key]


def generate(
    model_path: Path,
    messages: list[dict[str, str]],
    max_tokens: int = 256,
) -> tuple[str, int, int]:
    """Return (content, prompt_tokens, completion_tokens).

    Real backend if mlx_lm and a model are available. Echo fallback
    otherwise so the pipeline is always testable.
    """
    # Try the real backend
    if model_path.exists():
        try:
            model, tokenizer = _load(model_path)
            from mlx_lm import generate as mlx_generate

            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
            content = mlx_generate(
                model, tokenizer, prompt=prompt, max_tokens=max_tokens,
            )
            prompt_tokens = len(tokenizer.encode(prompt))
            completion_tokens = len(tokenizer.encode(content))
            return content, prompt_tokens, completion_tokens
        except Exception as e:
            # Fall through to echo, but record the reason
            reason = f"{type(e).__name__}: {e}"
    else:
        reason = f"model path does not exist: {model_path}"

    # Echo fallback — the pipeline runs, the response says why
    prompt_text = " ".join(m.get("content", "") for m in messages)
    content = f"[sovereign echo] backend unavailable ({reason})"
    return content, max(1, len(prompt_text) // 4), max(1, len(content) // 4)
''')
print("wrote sovereign/model.py")

# Rewrite node.py to use the model backend
Path("sovereign/node.py").write_text('''#!/usr/bin/env python3
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
    return {
        "status": "ok",
        "node_id": CONFIG["node_id"],
        "backend": CONFIG["backend"],
        "model": CONFIG["model"],
        "model_path": str(MODEL_PATH),
        "model_available": MODEL_PATH.exists(),
    }


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> dict[str, Any]:
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
''')
print("rewrote sovereign/node.py with real model backend")

# ============================================================== 2. A3/A4/A5 HARNESS
Path("research/harnesses/ablate_scale.py").write_text('''#!/usr/bin/env python3
"""A3 scale ablation + A5 bandwidth check.

Compares torch-mps-fp32 and mlx-fp16 at three model sizes.
Reports bytes-per-step and effective GB/s to answer whether the
workload is compute-bound or memory-bound.
"""
from __future__ import annotations

import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "datasets" / "ablation-scale.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)

HW = {"machine": platform.machine(), "platform": platform.platform(),
      "python": platform.python_version()}
DATE = datetime.now(timezone.utc).isoformat(timespec="seconds")


def torch_run(hidden: int, dtype_name: str = "float32", steps: int = 10):
    try:
        import torch
    except ImportError:
        return {"status": "unavailable", "reason": "torch not installed"}
    if not torch.backends.mps.is_available():
        return {"status": "unavailable", "reason": "mps not available"}
    dtype = {"float32": torch.float32, "float16": torch.float16}[dtype_name]
    try:
        model = torch.nn.Sequential(
            torch.nn.Linear(hidden, hidden),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden, hidden),
        ).to(device="mps", dtype=dtype)
        params = sum(p.numel() for p in model.parameters())
        opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
        x = torch.randn(4, hidden, device="mps", dtype=dtype)
        y = torch.randn(4, hidden, device="mps", dtype=dtype)
        for _ in range(2):
            opt.zero_grad()
            ((model(x) - y) ** 2).mean().backward()
            opt.step()
        t0 = time.time()
        for _ in range(steps):
            opt.zero_grad()
            ((model(x) - y) ** 2).mean().backward()
            opt.step()
        dt = time.time() - t0
        return {
            "status": "ok",
            "wall_seconds": dt,
            "seconds_per_step": dt / steps,
            "steps": steps,
            "parameters": params,
            "bytes_per_step": params * (4 if dtype_name == "float32" else 2) * 4,
            "runtime_version": torch.__version__,
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def mlx_run(hidden: int, dtype_name: str = "float16", steps: int = 10):
    try:
        import mlx.core as mx
        import mlx.nn as nn
        import mlx.optimizers as optim
    except ImportError as e:
        return {"status": "unavailable", "reason": f"mlx not installed: {e}"}
    dtype = {"float32": mx.float32, "float16": mx.float16, "bfloat16": mx.bfloat16}.get(dtype_name)
    if dtype is None:
        return {"status": "error", "reason": f"unknown dtype {dtype_name}"}

    class Model(nn.Module):
        def __init__(self, h):
            super().__init__()
            self.l1 = nn.Linear(h, h)
            self.l2 = nn.Linear(h, h)

        def __call__(self, x):
            return self.l2(nn.relu(self.l1(x)))

    try:
        model = Model(hidden)
        model.set_dtype(dtype)
        opt = optim.AdamW(learning_rate=1e-4)
        x = mx.random.normal((4, hidden)).astype(dtype)
        y = mx.random.normal((4, hidden)).astype(dtype)

        def loss_fn(m, x, y):
            return mx.mean((m(x) - y) ** 2)

        lg = nn.value_and_grad(model, loss_fn)
        for _ in range(2):
            loss, grads = lg(model, x, y)
            opt.update(model, grads)
            mx.eval(model.parameters(), opt.state)
        t0 = time.time()
        for _ in range(steps):
            loss, grads = lg(model, x, y)
            opt.update(model, grads)
            mx.eval(model.parameters(), opt.state)
        dt = time.time() - t0
        params = sum(p.size for _, p in mx.tree_flatten(model.parameters()))
        return {
            "status": "ok",
            "wall_seconds": dt,
            "seconds_per_step": dt / steps,
            "steps": steps,
            "parameters": params,
            "bytes_per_step": params * (4 if dtype_name == "float32" else 2) * 4,
            "runtime_version": getattr(mx, "__version__", "unknown"),
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}


SIZES = [(256, "1M"), (1024, "10M"), (4096, "100M")]

rows = []
for hidden, label in SIZES:
    for cond, fn in [
        ("torch-mps-fp32", lambda h=hidden: torch_run(h, "float32")),
        ("mlx-fp16",       lambda h=hidden: mlx_run(h, "float16")),
    ]:
        r = fn()
        row = {"ablation": "A3-scale", "scale": label, "hidden": hidden,
               "condition": cond, "date": DATE, "hardware": HW,
               "metric": "seconds_per_step"}
        row.update(r)
        rows.append(row)
        print(json.dumps(row))

print()
print("A5 — effective bandwidth at the largest size that returned ok:")
seen_scale = None
for r in rows:
    if r.get("scale") == "100M" and r.get("status") == "ok":
        seen_scale = "100M"
        bw = r["bytes_per_step"] / r["seconds_per_step"]
        print(f"  {r['condition']:<20} {r['bytes_per_step']/1e6:.1f} MB/step  ~{bw/1e9:.2f} GB/s")
if not seen_scale:
    print("  100M scale unavailable — check scale column above")

with OUT.open("a") as f:
    for r in rows:
        f.write(json.dumps(r) + "\\n")

print()
print(f"wrote {len(rows)} rows -> {OUT}")
''')
Path("research/harnesses/ablate_scale.py").chmod(0o755)
print("wrote research/harnesses/ablate_scale.py")

# ============================================================== 3. A1 FINDING
Path("research/findings/A1-runtime.md").write_text('''# A1 — Runtime Backend

**Hypothesis:** MLX is faster than torch-MPS for training steps on Apple
Silicon at small model sizes.

**Date:** 2026-10-14
**Nodes:** 1 (MacBook Pro, Mac16,5)
**Hardware:** Apple M4 Max, 16 cores (12P/4E), 128 GB unified memory
**Model:** tiny (1M params, 2 × Linear(256,256))

## Setup

`run_ablation.sh`, six conditions, 20 steps each, same model, same batch.
Warmup 3 steps before timing.

## Expected

MLX 1.5–3× faster than torch-MPS, per prior belief about unified memory
and ANE dispatch.

## Observed

| Condition | seconds_per_step | Relative |
|---|---|---|
| torch-mps-fp32 | 0.000390 | 1.00x (fastest) |
| torch-mps-fp16 | 0.000421 | 1.08x slower |
| torch-cpu-fp32 | 0.000701 | 1.80x slower |
| mlx-fp32 | 0.000702 | 1.80x slower |
| mlx-fp16 | 0.000579 | 1.48x slower |
| mlx-bf16 | 0.000675 | 1.73x slower |

Raw data: `research/datasets/ablation-runtime.jsonl`

## Interpretation

The hypothesis is **refuted at 1M parameters**. torch-MPS fp32 is fastest.
MLX is 33–44% slower. bf16 is slower than fp16 on this hardware, which is
the opposite of the usual GPU behavior.

The result may be an artifact of model size. At 1M parameters, kernel
launch overhead dominates compute, and the two runtimes dispatch
differently. The result does not predict behavior at 100M+ parameters
where memory bandwidth dominates.

## Next

A3 scale ablation at 1M, 10M, 100M parameters. If the ratio flips at
larger sizes, A1 is a toy artifact and MLX wins where it matters. If it
holds, torch-MPS is the correct backend at every size and the runtime
decision is settled.
''')
print("wrote research/findings/A1-runtime.md")

# register the finding
import json as _json
reg_path = Path("research/findings/REGISTER.json")
reg = _json.loads(reg_path.read_text())
if not any(f.get("id") == "A1-runtime" for f in reg["findings"]):
    reg["findings"].append({
        "id": "A1-runtime",
        "date": "2026-10-14",
        "hypothesis": "MLX faster than torch-MPS at small sizes",
        "result": "refuted at 1M params; torch-MPS fp32 fastest",
        "dataset": "research/datasets/ablation-runtime.jsonl",
        "next": "A3 scale ablation",
    })
    reg_path.write_text(_json.dumps(reg, indent=2))
    print("registered A1-runtime finding")

# ============================================================== 4. STRIP WHITESPACE
fixed = 0
for glob in ("*.py", "*.md", "*.json", "*.sh"):
    for p in Path(".").rglob(glob):
        if ".venv" in p.parts or ".git" in p.parts or "_archived" in p.parts:
            continue
        s = p.read_text()
        t = "\n".join(line.rstrip() for line in s.splitlines()) + "\n"
        if t != s:
            p.write_text(t)
            fixed += 1
print(f"stripped whitespace from {fixed} files")
PYEOF

echo
echo "=== run sovereign tests against real generate ==="
python -m pytest tests/test_sovereign_node.py -q 2>&1 | tail -8

echo
echo "=== full suite ==="
python -m pytest -q 2>&1 | tail -4
