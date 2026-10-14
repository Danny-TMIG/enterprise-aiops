#!/usr/bin/env python3
"""A6 — MLX per-step cost breakdown. Why does MLX scale linearly?"""
from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "datasets" / "ablation-mlx-breakdown.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten


def run(hidden: int, condition: str, steps: int = 10):
    class Model(nn.Module):
        def __init__(self, h):
            super().__init__()
            self.l1 = nn.Linear(h, h)
            self.l2 = nn.Linear(h, h)

        def __call__(self, x):
            return self.l2(nn.relu(self.l1(x)))

    model = Model(hidden)
    model.set_dtype(mx.float16)
    opt = optim.AdamW(learning_rate=1e-4)
    x = mx.random.normal((4, hidden)).astype(mx.float16)
    y = mx.random.normal((4, hidden)).astype(mx.float16)

    def loss_fn(m, x, y):
        return mx.mean((m(x) - y) ** 2)

    lg = nn.value_and_grad(model, loss_fn)

    # warmup
    for _ in range(2):
        loss, grads = lg(model, x, y)
        opt.update(model, grads)
        mx.eval(model.parameters(), opt.state)

    t0 = time.time()
    for _ in range(steps):
        if condition == "forward":
            out = model(x)
            mx.eval(out)
        elif condition == "forward_backward":
            loss, grads = lg(model, x, y)
            mx.eval(grads)
        elif condition == "forward_backward_update":
            loss, grads = lg(model, x, y)
            opt.update(model, grads)
            mx.eval(model.parameters())
        elif condition == "full":
            loss, grads = lg(model, x, y)
            opt.update(model, grads)
            mx.eval(model.parameters(), opt.state)
    dt = time.time() - t0
    params = sum(p.size for _, p in tree_flatten(model.parameters()))
    return {"seconds_per_step": dt / steps, "parameters": params, "condition": condition}


rows = []
for hidden, label in [(256, "0.13M"), (1024, "2.1M"), (4096, "33.6M")]:
    for cond in ("forward", "forward_backward", "forward_backward_update", "full"):
        r = run(hidden, cond)
        row = {
            "ablation": "A6-mlx-breakdown",
            "scale": label,
            "hidden": hidden,
            "condition": cond,
            "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **r,
        }
        rows.append(row)
        print(json.dumps(row))

with OUT.open("a") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"\nwrote {len(rows)} rows -> {OUT}")
