# docs/architecture/

## What is here

| File | Purpose |
|---|---|
| `ASF_ENVIRONMENT_REQUIREMENTS.md` | Environment record — assertions, open decisions, verification |
| `SPEC_TO_CODE.md` | Generated map from each FAS logical component to its directory |
| `FILE_REFERENCE.md` | File-by-file reference |
| `BARE_VS_SLUGGED.md` | Note on the two-directory-per-component pattern |
| `ARCHITECT_ONBOARDING.md` | Onboarding for a new architect |

## Regeneration

`SPEC_TO_CODE.md` is generated:

    python3 tooling/validation/generate_spec_to_code.py

The rest are hand-written.

## What belongs here

Onboarding, reference, and diagrams. Not per-component documentation, not
decision records, not specification text. This directory describes the
architecture as it currently exists.
