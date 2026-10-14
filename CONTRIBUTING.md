# Contributing

## Before you start

Read docs/AUTHORITY.md.

## Ground rules

1. Keep the gates green.
2. Respect the tree (catalog/TARGET_TREE.txt).
3. Contracts are versioned by $id.
4. Public APIs under src/public/ are stable.
5. No secrets.

## Gates

    python3 tooling/master_orchestrator.py
    python3 tooling/platform_validate.py
    python3 tooling/validate_profiles.py
    python3 tooling/validation/check_federation_gate.py
    python3 -m pytest tests/ -q
    python3 integration/e2e/test_full_stack_diagnostic.py

## Adding a component

1. Create components/<layer>/<ID>-<slug>/.
2. Populate component.json: id, name, description, version, status,
   inputs, outputs, state_owner, invariants.
3. Put real code under src/public/ with docstrings.
4. Register in catalog/inventories/components.json.
5. Add a test under tests/unit/components/.
6. Run the gates.

## Commit style

Conventional prefix, imperative mood.

## Readmes

tooling/release/generate_readmes.py derives per-component readmes.
