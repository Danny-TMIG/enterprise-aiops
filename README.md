# Aether Fabric — Sovereign AI Operations Platform

A layered, contract-first platform for governed AI operations. Three
constitutional layers — Aether Cognition (AX), Aether Govern (AG), and
Aether Compute (AC) — are composed into deployable units and validated by
a monorepo pipeline.

## What this repository is

- A monorepo of 75 components across three layers, each with a declared
  contract, a public API surface, and a component.json manifest.
- A governed runtime: every action is authorized, every state transition
  is recorded, every outcome is correlated and verifiable.
- A buildable system: deploy/units/*/unit.json describes deployable units;
  deploy/profiles/*/profile.json describes deployment topologies.

## What this repository is not

- Not a stubbed demo. Components under components/*/*/src/public/ are real.
- Not a single-service app. The pipeline is orchestrated by
  tooling/master_orchestrator.py.
- Not complete. See docs/STATUS.md.

## Requirements

- Python >= 3.11 (the codebase uses typing.Self).
- yamllint and shellcheck for tooling/platform_validate.py.
- macOS or Linux.

## Getting started

    git clone https://github.com/Danny-TMIG/Aether-Fabric-Soverign-V1.0.git
    cd Aether-Fabric-Soverign-V1.0
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
    python3 tooling/master_orchestrator.py

## Repository map

- components/ax/  Aether Cognition (21)
- components/ag/  Aether Govern (24)
- components/ac/  Aether Compute (30)
- contracts/      Interface schemas
- catalog/        Inventories and requirement maps
- deploy/         Units, profiles, releases
- integration/    Cross-layer, authority, sovereignty, e2e
- libraries/      Shared internal libraries
- tooling/        Bootstrap, validation, release
- docs/           Authority, status, architecture, decisions
- examples/       Synthetic fixtures
- _archive/       Superseded artifacts

## Gates

    python3 tooling/master_orchestrator.py
    python3 tooling/platform_validate.py
    python3 tooling/validate_profiles.py
    python3 tooling/validation/check_federation_gate.py
    python3 -m pytest tests/ -q
    python3 integration/e2e/test_full_stack_diagnostic.py

## Governance

docs/AUTHORITY.md is authoritative. docs/STATUS.md tracks maturity.
