#!/usr/bin/env python3
"""Measure one local training step. No network. No sharding.

This is the baseline. Run it on a single machine before any distributed
claim. The number it produces is the floor.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from datetime import datetime, timezone


def measure_locally(model_name: str, steps: int = 10) -> dict:
    """Time N forward+backward passes on whatever hardware is present."""
    try:
        import torch
    except ImportError:
        return {"error": "torch not installed"}

    device = "cuda" if torch.cuda.is_available() else "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu"

    # Minimal model: 1M parameters. Scales to real sizes by substitution.
    model = torch.nn.Sequential(
        torch.nn.Linear(256, 256),
        torch.nn.ReLU(),
        torch.nn.Linear(256, 256),
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)

    x = torch.randn(32, 256, device=device)
    y = torch.randn(32, 256, device=device)

    t0 = time.time()
    for _ in range(steps):
        opt.zero_grad()
        loss = ((model(x) - y) ** 2).mean()
        loss.backward()
        opt.step()
    dt = time.time() - t0

    return {
        "device": device,
        "model": model_name,
        "steps": steps,
        "wall_seconds": dt,
        "seconds_per_step": dt / steps,
        "torch_version": torch.__version__,
    }


if __name__ == "__main__":
    import sys
    result = measure_locally(sys.argv[1] if len(sys.argv) > 1 else "tiny")
    result["date"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(json.dumps(result, indent=2))
