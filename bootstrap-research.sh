#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

mkdir -p research/{experiments,findings,protocols,harnesses,datasets}
mkdir -p research/experiments/{comm,econ,verif,scale}

# ============================================================ PROTOCOL
cat > research/PROTOCOL.md <<'MD'
# Distributed Training Research Protocol

## Scope

Evaluate whether consumer devices (laptops, phones, single-GPU workstations)
can cooperatively train or serve frontier-class models. "Frontier-class"
means model sizes where current centralized training requires 100M+ USD of
compute. The question is whether a different topology changes the cost curve.

## Hypotheses (each is falsifiable)

H1. Communication, not compute, is the binding constraint for >50B models
    over consumer networks (1 Gbps down, 50 Mbps up).
    Falsification: if compute time exceeds communication time on real
    hardware over 30-day runs, H1 is false.

H2. DiLoCo-style outer-loop averaging (local steps H>=500, pseudo-gradient
    sync) preserves downstream task performance when trained across consumer
    nodes.
    Falsification: nanochat+DiLoCo result showed downstream collapse despite
    stable pretraining loss [citation:27]. H2 may already be falsified.

H3. Verification of contributed work is possible without full recomputation.
    Falsification: if the cheapest verification costs more than 10% of the
    work being verified, the scheme is not economically viable.

H4. Consumer GPUs (3060-class, 12GB VRAM) can host a productive shard of a
    70B+ model when sharded by layer.
    Falsification: Petals shows 1 step/sec on BLOOM-176B, which is
    interactive but not training-throughput [citation:8].

## Method

1. Baseline measurement: one laptop, one model, one epoch.
2. Shard measurement: 3+ laptops, same model, sharded.
3. Communication cost: bytes exchanged per parameter update.
4. Convergence: loss curve vs. centralized baseline over equal tokens.
5. Economic viability: dollars per token vs. cloud equivalent.

## Data Readiness

Every experiment writes a JSONL row:

    {"exp_id", "date", "nodes", "gpu_class", "model", "bytes_sent",
     "bytes_received", "tokens_processed", "wall_seconds", "final_loss",
     "notes"}

Nothing is a finding until it has a row. Nothing is a conclusion until
three rows agree.
MD

# ============================================================ EXPERIMENT TEMPLATE
cat > research/experiments/TEMPLATE.md <<'MD'
# Experiment: <name>

**Hypothesis:** <which H1-H4>
**Date:** <ISO>
**Nodes:** <count and hardware>
**Model:** <architecture and size>

## Setup
<exact commands>

## Expected
<what we predict before running>

## Observed
<what actually happened>

## Raw data
<path to JSONL>

## Interpretation
<what this rules in, rules out, or leaves open>

## Next
<the follow-up experiment or the falsification>
MD

# ============================================================ FINDINGS REGISTER
cat > research/findings/REGISTER.json <<'JSON'
{
  "schema_version": "1.0",
  "findings": [],
  "note": "One entry per verified finding. Each must cite an experiment ID and a JSONL row."
}
JSON

# ============================================================ HARNESS STUB
cat > research/harnesses/measure.py <<'PY'
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
PY
chmod +x research/harnesses/measure.py

# ============================================================ README
cat > research/README.md <<'MD'
# Distributed Training Research

This directory is a research scaffold, not a working distributed system.

## What exists

| Path | Purpose |
|---|---|
| `PROTOCOL.md` | Hypotheses, method, data format |
| `experiments/` | One markdown file per experiment |
| `findings/` | JSON register of verified findings |
| `harnesses/` | Code that measures |
| `datasets/` | Raw JSONL from runs |

## What does not exist

- No working distributed trainer
- No sharding implementation
- No verification scheme
- No economic model

Those are the outputs of the research, not the inputs.

## How to start

Run the baseline:

    python3 research/harnesses/measure.py

It times 10 training steps on whatever hardware you have. That number is
your floor. Every distributed claim is measured against it.

## Why this is a bootstrap

Because a research program cannot be delivered as code. It can only be
delivered as a structured container for findings, plus the discipline to
fill it. The container is here. The findings are not.
MD

echo "research scaffold written to research/"
ls -1 research/
