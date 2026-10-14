# The A–Z Economic Control Plane

## Provenance

This specification extends *The Economic Control Plane: A Provider-Neutral
Architecture for Governed Work Allocation Across Human, Software, and AI
Execution*. The paper names four control layers — A Contract, B
Constraints, C Market, D Receipt. This document extends the structure to
twenty-six layers, each with a unique name, unique attributes, and a
declared position in a causal graph.

## The 26 layers

| Letter | Name | Role | Reads | Writes |
|---|---|---|---|---|
| **A** | Contract | Define | input | ExecutionContract |
| **B** | Constraints | Govern | A | ConstraintBinding |
| **C** | Norm | Calibrate | input, A | NormCurve |
| **D** | Market | Allocate | A, B, C | AllocationDecision |
| **E** | Receipt | Prove | D | EconomicReceipt |
| **F** | Envelope | Frame | A, B | CommonEnvelope |
| **G** | Fidelity | Measure | A, B, D | FidelityScore |
| **H** | Gate | Admit | A, B, G | GateDecision |
| **I** | Identity | Bind | A | IdentityBinding |
| **J** | Handle | Route | D, H, I | RoutingHandle |
| **K** | Jurisdiction | Scope | B, J | JurisdictionScope |
| **L** | Kind | Classify | input, A | WorkKind |
| **M** | Ledger | Record | ALL | LedgerEntry |
| **N** | Meter | Count | M | MeterReading |
| **O** | Oversight | Supervise | H, B | OversightPlan |
| **P** | Provenance | Trace | ALL | ProvenanceChain |
| **Q** | Quality | Assure | O | QualityVerdict |
| **R** | Risk | Bound | K, Q | RiskBound |
| **S** | Shadow | Preview | D, G | ShadowProposal |
| **T** | Trust | Attest | J, M, P | Attestation |
| **U** | Usage | Attribute | N | UsageAttribution |
| **V** | Variance | Compare | C, U | VarianceReport |
| **W** | Witness | Corroborate | E, T, P | WitnessVerdict |
| **X** | eXception | Handle | ANY_REJECTION | ExceptionRecord |
| **Y** | Yield | Realize | Q, V | YieldReport |
| **Z** | Zenith | Close | ALL | ZenithSeal |

## Pollination

Layers do not merely chain. They pollinate. A layer may read from any
earlier layer whose artifact exists for the run, but only at declared
boundaries. A layer that reads from a downstream layer is a bug: it breaks
causality.

The read graph is dense. The write graph is a chain. Every layer writes
exactly one artifact; every layer reads zero or more declared inputs.

The runner enforces this. `PollinationGraph.validate_path()` rejects any
path where a layer reads from a layer not earlier in the path.

## Prefix paths and skip paths

A prefix path is A, AB, ABC, …, ABCDEFGHIJKLMNOPQRSTUVWXYZ — 26 legal
chains.

A skip path is any subset of letters that preserves the read order. For
example, `ABD` is illegal because D reads C. But `LCD` is legal if the
caller knows L reads A, C reads A, and D reads A, B, C. The validator
checks this automatically.

## The runner

`control_plane.Runner` walks a path, calls each layer in order, threads
context between them, and halts on the first non-PASS. Every step is
recorded. Every artifact is stored.

    python -m control_plane.cli --path ABCD --request examples/request.json

The CLI writes `run-evidence.json` containing every step, every artifact,
and the request hash.

## The four original control layers

A, B, C, and D remain the layers named by the paper. Their attributes are
identical to the paper\'s specification:

- **A Contract** derives the execution contract from the work request
- **B Constraints** binds the contract to concrete constraint values
- **C Market** is now **Norm** — the calibration curve that allocation
  requires as input; the layer formerly at C is now **D Market**
- **D Receipt** is now **E Receipt** — it computes the dollar delta

The letter shift from the paper was forced by acycicity: the paper\'s
Market layer needs a Norm curve, and a Norm curve cannot be produced after
the layer that consumes it.

## Prompts

Every layer has a 250-word prompt in `prompts/<letter>-<name>.md`. The
prompt is the *implementation* of the layer. The layer module is the
*interface*. Both are required.

Prompts use load-bearing grammar: every word does work. No filler, no
hedging, no self-reference. The structure is uniform: role, context, task,
procedure, constraints, failure modes, verification, evidence.

## Tests

Four test files:

| File | Checks |
|---|---|
| `tests/test_layers.py` | 26 layer classes registered, artifacts valid, schemas exist, prompts exist |
| `tests/test_pollination.py` | Acyclic, all prefix paths validate, illegal paths rejected |
| `tests/test_paths.py` | End-to-end run of prefix paths, artifacts present, halt recorded |
| `tests/test_prompts.py` | 26 prompts, word count in range, no forbidden phrases |

Run all:

    python -m pytest tests/test_layers.py tests/test_pollination.py tests/test_paths.py tests/test_prompts.py -q

## What this is not

- It is not the paper. The paper names four layers. This names 26.
- It is not complete. Every layer\'s `_produce` method returns a
  placeholder payload. Real behavior substitutes into each layer\'s
  `_produce` without changing the contract, the prompt, the schema, or
  the runner.
- It is not deployed. The runner executes in-process. There is no
  persistence beyond the evidence file.
- It is not validated against real work. No shadow-mode trial has run.

## What would make it real

1. Replace each layer\'s `_produce` with an LLM-backed implementation that
   consumes the layer\'s prompt and returns a payload matching the schema.
2. Add evidence-chain Merkle composition across layers (already in the
   swarm module; needs porting).
3. Run a shadow-mode trial on one domain — the paper names eleven.
4. Compute a real economic receipt for one unit of work.
