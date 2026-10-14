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
