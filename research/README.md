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
