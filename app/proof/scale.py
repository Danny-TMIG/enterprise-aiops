"""Claim 4: one M4 Max is one M4 Max."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def model_size() -> tuple:
    hf = Path.home() / ".cache" / "huggingface" / "hub"
    if not hf.exists():
        return 0, "no HF cache"
    size = 0
    for p in hf.rglob("model*.safetensors"):
        size += p.stat().st_size
    return size, f"{size / (1024 ** 3):.2f} GiB weights on disk"


def measure_throughput() -> tuple:
    from app.dispatch.models.base import ModelRequest
    from app.dispatch.models.local_mlx import LocalMLXProvider, _mlx_available
    if not _mlx_available():
        return 0.0, "MLX unavailable"
    p = LocalMLXProvider("scale-bench")
    req = ModelRequest(task="coding",
                       prompt="Write a one-line Python function that adds 1.",
                       max_tokens=64, temperature=0.0)
    t0 = time.time()
    r = p.complete(req)
    dt = time.time() - t0
    out = (r.usage or {}).get("output_tokens", 0) or 1
    tps = out / max(dt, 1e-3)
    return tps, f"{out} tokens in {dt:.2f}s = {tps:.1f} tok/s"


def main() -> int:
    print("── claim 4: one M4 Max is one M4 Max ──")
    size, sz = model_size()
    print(f"  model: {sz}")
    tps, tp = measure_throughput()
    print(f"  throughput: {tp}")

    per_artifact = 6 * 32 + 192
    if tps > 0:
        sec_per_artifact = per_artifact / tps
        per_hour = 3600 / sec_per_artifact
        print(f"  per artifact: ~{per_artifact} tokens ≈ {sec_per_artifact:.1f}s")
        print(f"  artifacts/hour (1 worker): {per_hour:.0f}")
        print(f"  artifacts/hour (4 workers): {per_hour * 4:.0f}")
    else:
        per_hour = 0
        print("  artifacts/hour: unmeasurable")

    print(f"  CPU count: {os.cpu_count()}")
    print("  parallelism: 1 MLX model, single GPU")
    print("  horizontal scaling: N/A without distributed runtime")
    print("  failure domain: 1 machine")
    print()
    if tps > 0:
        print(f"  verdict: ceiling = 1 machine × {tps:.0f} tok/s × "
              f"{per_hour:.0f} artifacts/h")
    else:
        print("  verdict: throughput unmeasurable on this host")
    return 0


if __name__ == "__main__":
    sys.exit(main())
