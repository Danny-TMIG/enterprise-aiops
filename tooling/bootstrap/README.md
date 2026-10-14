# tooling/bootstrap/

## What is here

Scripts that stand up a working environment from a clean checkout.

## What belongs here

- `bootstrap.sh` — clone, venv, install, verify
- `run_all.sh` — run the full pipeline locally

## Rules

- **Idempotent.** Running twice produces the same result as running once.
- **No network beyond package installation.** No fetching files from
  external services.
- **Print clear success or failure.** A bootstrap that silently fails is
  worse than no bootstrap.
- **Point at the verification path.** A successful bootstrap ends by
  running `status.py` and `pytest` so the user knows it worked.
