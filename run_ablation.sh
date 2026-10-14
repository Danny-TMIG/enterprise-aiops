#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

pip install --quiet mlx 2>/dev/null || echo "mlx install failed or not needed"

python3 - <<'PYEOF'
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "aether"
OUT = ROOT / "research" / "datasets" / "ablation-runtime.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)

HW = {
    "machine": platform.machine(),
    "platform": platform.platform(),
    "python": platform.python_version(),
}
DATE = datetime.now(timezone.utc).isoformat(timespec="seconds")


def torch_run(device, dtype_name, steps=20):
    try:
        import torch
    except ImportError:
        return {"status": "unavailable", "reason": "torch not installed"}

    if device == "mps" and not torch.backends.mps.is_available():
        return {"status": "unavailable", "reason": "mps not available"}

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[dtype_name]

    try:
        model = torch.nn.Sequential(
            torch.nn.Linear(256, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 256),
        ).to(device=device, dtype=dtype)
        opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
        x = torch.randn(32, 256, device=device, dtype=dtype)
        y = torch.randn(32, 256, device=device, dtype=dtype)

        for _ in range(3):
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
            "runtime_version": torch.__version__,
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def mlx_run(dtype_name, steps=20):
    try:
        import mlx.core as mx
        import mlx.nn as nn
        import mlx.optimizers as optim
    except ImportError as e:
        return {"status": "unavailable", "reason": f"mlx not installed: {e}"}

    dtype = {"float32": mx.float32, "float16": mx.float16,
             "bfloat16": mx.bfloat16}.get(dtype_name)
    if dtype is None:
        return {"status": "error", "reason": f"unknown dtype {dtype_name}"}

    class Tiny(nn.Module):
        def __init__(self):
            super().__init__()
            self.l1 = nn.Linear(256, 256)
            self.l2 = nn.Linear(256, 256)

        def __call__(self, x):
            return self.l2(nn.relu(self.l1(x)))

    try:
        model = Tiny()
        model.set_dtype(dtype)
        opt = optim.AdamW(learning_rate=1e-4)
        x = mx.random.normal((32, 256)).astype(dtype)
        y = mx.random.normal((32, 256)).astype(dtype)

        def loss_fn(m, x, y):
            return mx.mean((m(x) - y) ** 2)

        loss_and_grad = nn.value_and_grad(model, loss_fn)

        for _ in range(3):
            loss, grads = loss_and_grad(model, x, y)
            opt.update(model, grads)
            mx.eval(model.parameters(), opt.state)

        t0 = time.time()
        for _ in range(steps):
            loss, grads = loss_and_grad(model, x, y)
            opt.update(model, grads)
            mx.eval(model.parameters(), opt.state)
        dt = time.time() - t0

        return {
            "status": "ok",
            "wall_seconds": dt,
            "seconds_per_step": dt / steps,
            "steps": steps,
            "runtime_version": getattr(mx, "__version__", "unknown"),
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}


CONDITIONS = [
    ("A1-runtime", "torch-mps-fp32", lambda: torch_run("mps", "float32")),
    ("A1-runtime", "torch-mps-fp16", lambda: torch_run("mps", "float16")),
    ("A1-runtime", "torch-cpu-fp32", lambda: torch_run("cpu", "float32")),
    ("A1-runtime", "mlx-fp32",       lambda: mlx_run("float32")),
    ("A1-runtime", "mlx-fp16",       lambda: mlx_run("float16")),
    ("A2-precision", "mlx-bf16",     lambda: mlx_run("bfloat16")),
]

rows = []
for ablation, condition, fn in CONDITIONS:
    r = fn()
    row = {
        "ablation": ablation,
        "condition": condition,
        "date": DATE,
        "hardware": HW,
        "metric": "seconds_per_step",
    }
    row.update(r)
    rows.append(row)
    print(json.dumps(row, indent=2))

with OUT.open("a") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")

print()
print(f"wrote {len(rows)} rows -> {OUT}")

# print a compact table
print()
print(f"{'condition':<22} {'status':<12} {'seconds_per_step':<20}")
print("-" * 56)
for r in rows:
    v = r.get("seconds_per_step")
    vs = f"{v:.6f}" if isinstance(v, (int, float)) else "-"
    print(f"{r['condition']:<22} {r['status']:<12} {vs:<20}")

# compute ratios where both sides are ok
print()
print("ratios (lower is faster):")
for r in rows:
    if r["status"] == "ok" and r["condition"].startswith("mlx"):
        mps = next((x for x in rows if x["condition"] == "torch-mps-fp32" and x["status"] == "ok"), None)
        if mps:
            ratio = mps["seconds_per_step"] / r["seconds_per_step"]
            print(f"  torch-mps-fp32 / {r['condition']:<16} = {ratio:.2f}x")
PYEOF
