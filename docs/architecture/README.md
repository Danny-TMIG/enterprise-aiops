# Architecture Documents

Files in this directory:

| File | Purpose |
|---|---|
| `ARCHITECT_ONBOARDING.md` | Onboarding for a new architect; reading order, contracts, environment, open decisions |
| `SPEC_TO_CODE.md` | Generated map from each FAS logical component to its directory in the tree |
| `FILE_REFERENCE.md` | File-by-file reference for the repository, 250 words per entry |
| `ASF_ENVIRONMENT_REQUIREMENTS.md` | Environment record — assertions, targets, limitations, assumptions |

Regenerate `SPEC_TO_CODE.md` with:

    python3 tooling/validation/generate_spec_to_code.py
