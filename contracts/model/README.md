# contracts/model/

Model-integration contracts. Each schema closes a gap between model
documentation and the ASF boundary contract set.

## Files

| File | Closes | Gap |
|---|---|---|
| `model-card.schema.json` | G1, G2, G3, G4, G5, G10 | Parameter count, modality, quantization, license, compute budget, evidence obligations |
| `model-classification-binding.schema.json` | G11 | Model classification ceiling enforcement |

## Deferred gaps

Four gaps remain blocked on FAS decisions:

| Gap | Waiting on |
|---|---|
| G6 Context construction | COG-DEC-009 |
| G7 Fallback rules | COG-DEC-010 |
| G8 Serving pattern | CMP-DEC-003 |
| G9 Substrate qualification | COG-DEC-007 |

Their shape is recorded in `docs/architecture/MODEL_GAP_CLOSURES.md`.
