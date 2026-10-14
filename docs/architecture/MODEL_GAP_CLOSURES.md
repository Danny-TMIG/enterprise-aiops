# Model Gap Closures

## Ready now

| Gap | Closed by | Test |
|---|---|---|
| G1 Parameter count | `parameter_count` object | `test_model_card_requires_parameter_count` |
| G2 Modality | `modality` enum array | `test_model_card_requires_modality` |
| G3 Quantization | `quantization.supported` | `test_model_card_declares_quantization` |
| G4 License | `license.spdx` | `test_model_card_requires_spdx` |
| G5 Compute budget | `compute_budget` object | `test_model_card_declares_compute_budget` |
| G10 Evidence obligations | `evidence_obligations` array | `test_model_card_requires_evidence` |
| G11 Classification ceiling | `ModelClassificationBinding` | `test_classification_ceiling_enforced` |

## Deferred

| Gap | Waiting on | Shape recorded |
|---|---|---|
| G6 Context construction | COG-DEC-009 | `ContextAssemblyRecord` |
| G7 Fallback rules | COG-DEC-010 | `fallback_is_eligible` predicate |
| G8 Serving pattern | CMP-DEC-003 | Profile-aware constraint on model card |
| G9 Substrate qualification | COG-DEC-007 | `QualificationRecord` |
