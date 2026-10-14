# integration/e2e/

## What is here

| File | Purpose |
|---|---|
| `test_full_stack_diagnostic.py` | The cross-layer end-to-end diagnostic |
| `test_sovereign_e2e.py` | Sovereign path end-to-end test |

## The diagnostic

`test_full_stack_diagnostic.py` is the executable definition of "ASF runs."
It exercises one path from each layer:

| Layer | What it checks |
|---|---|
| `[AC]` | Telemetry captured |
| `[AG]` | WORM state transition recorded and chain verified |
| `[AG]` | Governance registry version chain verified |
| `[AG]` | Decision/outcome correlation closed and verified |
| `[AX]` | Cognitive runtime completed 6 stages |

On success it prints five checkmarks and `💯 [SUCCESS]`. Anything else
means the run did not complete.

## Running it

    make test
    # or
    python3 integration/e2e/test_full_stack_diagnostic.py

## Relationship to the orchestrator

`tooling/master_orchestrator.py` invokes this diagnostic as its second
stage. A passing orchestrator run means this file passed.
