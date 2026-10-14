#!/usr/bin/env python3
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
        f.write(json.dumps(r) + "\n")

print()
print(f"wrote {len(rows)} rows -> {OUT}")
