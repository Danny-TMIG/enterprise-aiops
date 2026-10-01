# Ten Moats — Unique Core Algorithms / Architectures

A live registry. The doc is a projection of
`app/atlas/moats.py`. Edit the data in that module and
re-run `python3 -m app.atlas.moats_cli --write` to regenerate.

Total moats: **11**.

| # | Moat | Value class | Status | Implementers | Residuals |
|---|------|-------------|--------|--------------|-----------|
| 1 | Braided multimodal fusion engine | patent (novel fusion rules) | partial | `app.combinator`, `app.math.graph`, `app.nested` | `K-27`, `M-23`, `Z-12` |
| 2 | Self-healing orchestration with causal tracing | patent + operations | partial | `app.autonomy.healer`, `app.autonomy.watchdog`, `app.meta.loop`, `app.moat.axes` | `X-01`, `X-04`, `X-08`, `T-25` |
| 3 | Proprietary datasets and curation pipeline | trade-secret | partial | `app.delta.corpus`, `app.delta.curriculum`, `app.backrooms` | `I-02`, `M-18`, `S-11` |
| 4 | Fine-tuning + quantization for local hardware | performance + product differentiation | partial | `app.dispatch.models.local_mlx`, `app.origami.library`, `app.reality` | `P-14`, `I-02`, `T-19` |
| 5 | Reproducible auditable build + signed SBOMs | compliance + enterprise trust | partial | `app.seed.manifest`, `app.seed.seal`, `app.proof.regulatory`, `app.reality.install` | `T-21`, `T-28`, `T-29`, `K-15` |
| 6 | Policy-driven safety + compliance platform | regulatory readiness | partial | `app.moat.runtime`, `app.meta.observer`, `app.federation.privacy`, `app.canon.commandments` | `G-13`, `T-31`, `T-32` |
| 7 | Novel UI/UX and developer platform (SDK + API) | network effect + licensing | partial | `app.reconfig`, `app.engines`, `app.train` | `T-24`, `D-15`, `G-01` |
| 8 | Hybrid trust: federated + local with DP | privacy-first customers | partial | `app.federation.consensus`, `app.federation.privacy`, `app.federation.provenance`, `app.federation.security` | `D-01`, `D-02`, `G-09`, `S-06` |
| 9 | Hardware kernels: M-series, AVX, CUDA, WebGPU | performance + patent | planned | `app.math`, `app.ddlong.dd`, `app.substrate` | `C-22`, `P-14`, `H-14` |
| 10 | Orchestration semantics / declarative braid language | platform lock-in + patent | partial | `app.reconfig.rules`, `app.reconfig.codeal`, `app.chain`, `app.cst` | `K-27`, `C-19`, `T-11` |
| 11 | Ecosystem: reference apps, templates, marketplace | revenue + adoption | partial | `app.proprietary`, `app.frontier`, `app.puzzles`, `app.canon` | `G-01`, `N-06`, `N-16` |

## Details

### 1. Braided multimodal fusion engine

**Value class:** patent (novel fusion rules)  
**Status:** partial

Deterministically fuses vision/audio/text/quantum outputs into a single latent for reasoning. Novel fusion rules, gating, and attention sparsity patterns. The braid is the operational semantics: interleaved channels that commute under a fixed crossing invariant.

Implemented by:
- `app.combinator (braid as graph reduction)`
- `app.math.graph (fusion topology)`
- `app.nested (multi-level fusion)`

Grounded in residuals: `K-27`, `M-23`, `Z-12`

### 2. Self-healing orchestration with causal tracing

**Value class:** patent + operations  
**Status:** partial

Intent-aware restart and placement decisions driven by causal traces, not liveness checks. Tie into cost, energy, and latency models. Restart a node only when the causal chain that failed is understood; otherwise escalate.

Implemented by:
- `app.autonomy.healer`
- `app.autonomy.watchdog`
- `app.meta.loop`
- `app.moat.axes`

Grounded in residuals: `X-01`, `X-04`, `X-08`, `T-25`

### 3. Proprietary datasets and curation pipeline

**Value class:** trade-secret  
**Status:** partial

High-quality domain-specific datasets: curated, deduplicated, fingerprinted. Automated lineage, provenance, labeling. Synthetic augmentation to extend real data safely.

Implemented by:
- `app.delta.corpus (BM25 retrieval)`
- `app.delta.curriculum (SFT/DPO emission)`
- `app.backrooms (residue store)`

Grounded in residuals: `I-02`, `M-18`, `S-11`

### 4. Fine-tuning + quantization for local hardware

**Value class:** performance + product differentiation  
**Status:** partial

Automated quantization / pruning producing small accurate models for WebGPU / Apple Silicon / CPU. Guaranteed latency-accuracy tradeoffs. Reproducible deterministic builds.

Implemented by:
- `app.dispatch.models.local_mlx`
- `app.origami.library (grammar compilation)`
- `app.reality (environment reproducibility)`

Grounded in residuals: `P-14`, `I-02`, `T-19`

### 5. Reproducible auditable build + signed SBOMs

**Value class:** compliance + enterprise trust  
**Status:** partial

Deterministic stage-0 to stage-N builds. Content-addressed artifacts. SBOMs. Cryptographic signing. Supply-chain attestations (in-toto).

Implemented by:
- `app.seed.manifest`
- `app.seed.seal`
- `app.proof.regulatory`
- `app.reality.install`

Grounded in residuals: `T-21`, `T-28`, `T-29`, `K-15`

### 6. Policy-driven safety + compliance platform

**Value class:** regulatory readiness  
**Status:** partial

Policy DSL tailored to AI behaviours: data access, hallucination gates, decision logging. Automatic policy drift detection. Audit reports.

Implemented by:
- `app.moat.runtime`
- `app.meta.observer`
- `app.federation.privacy`
- `app.canon.commandments`

Grounded in residuals: `G-13`, `T-31`, `T-32`

### 7. Novel UI/UX and developer platform (SDK + API)

**Value class:** network effect + licensing  
**Status:** partial

Multi-language SDKs. Reproducible local sandboxes. One-click orchestration CLI. Turn runtime capabilities into platform lock-in.

Implemented by:
- `app.reconfig (intent → code)`
- `app.engines (parallel grid runner)`
- `app.train (curriculum + metrics)`

Grounded in residuals: `T-24`, `D-15`, `G-01`

### 8. Hybrid trust: federated + local with DP

**Value class:** privacy-first customers  
**Status:** partial

Federated learning orchestration keeping data local, aggregating updates securely. Differential privacy for safe model updates.

Implemented by:
- `app.federation.consensus`
- `app.federation.privacy`
- `app.federation.provenance`
- `app.federation.security`

Grounded in residuals: `D-01`, `D-02`, `G-09`, `S-06`

### 9. Hardware kernels: M-series, AVX, CUDA, WebGPU

**Value class:** performance + patent  
**Status:** planned

Hand-tuned kernels for Apple M-series, AVX2/AVX512, CUDA, and WebGPU shaders for common ops. Performance claims backed by reproducible benchmarks.

Implemented by:
- `app.math (numerical primitives)`
- `app.ddlong.dd (double-double arithmetic)`
- `app.substrate (RAM / streaming)`

Grounded in residuals: `C-22`, `P-14`, `H-14`

### 10. Orchestration semantics / declarative braid language

**Value class:** platform lock-in + patent  
**Status:** partial

Compact declarative language for braid workflows: data pipelines + model orchestration + policies + cost constraints. Compiles to runtime. Language IP is a high-value product.

Implemented by:
- `app.reconfig.rules (rule language)`
- `app.reconfig.codeal (Code-AL IR)`
- `app.chain (36-role composition)`
- `app.cst (predicate loop)`

Grounded in residuals: `K-27`, `C-19`, `T-11`

### 11. Ecosystem: reference apps, templates, marketplace

**Value class:** revenue + adoption  
**Status:** partial

Reference applications, case studies, paid templates, partner integrations. Signing and trust marketplace for models.

Implemented by:
- `app.proprietary (registry of vendor integrations)`
- `app.frontier (research profiles)`
- `app.puzzles + app.engines + app.train (demonstrators)`
- `app.canon (governance docs)`

Grounded in residuals: `G-01`, `N-06`, `N-16`

---

## Status summary

| Status | Count |
|--------|-------|
| partial | 10 |
| planned | 1 |

## The register's own entry

Moats 1 through 11 all terminate at `Ω`. The claim that
this set is complete cannot be decided from inside the
set. Adding moat 12 is the act of proceeding.
