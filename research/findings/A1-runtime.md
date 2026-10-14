# A1 — Runtime Backend

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
