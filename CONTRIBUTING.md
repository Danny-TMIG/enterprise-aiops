# Contributing

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    pip install -e .

## Checks

    ruff check .
    mypy aiops_platform
    pytest -q
