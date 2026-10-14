# tooling/validation/

## What is here

| File | Purpose |
|---|---|
| `status.py` | Repository health check — GIT, TREE, SIZE, VERDICT |
| `spec_audit.py` | Specification conformance audit |
| `platform_validate.py` | Validate `platform/` — YAML, JSON, shell |
| `validate_profiles.py` | Validate `deploy/profiles/` — schema and cross-references |
| `check_federation_gate.py` | Allow the federation flip only when every gate is satisfied |
| `validate_tree.py` | Monorepo structural linter — reads `catalog/components.json` |
| `audit_attestation.py` | Attestation audit |
| `generate_spec_to_code.py` | Regenerate `docs/architecture/SPEC_TO_CODE.md` |

## Rules

- **Read-only.** None of these mutate the repo or state.
- **Deterministic.** Same inputs, same output.
- **Exit codes matter.** `0` on success, non-zero on failure. `status.py`
  returns 1 when VERDICT is ATTENTION.
- **No side effects.** No writes to `catalog/`, `contracts/`, or any
  component. Writes go only to `deploy/ledgers/` when the orchestrator
  seals a run.
