## Summary

## Layers affected

- [ ] AX
- [ ] AG
- [ ] AC
- [ ] Contracts
- [ ] Catalog
- [ ] Deploy
- [ ] Integration
- [ ] Tooling
- [ ] Docs

## Gates

    python3 tooling/master_orchestrator.py
    python3 tooling/platform_validate.py
    python3 tooling/validate_profiles.py
    python3 tooling/validation/check_federation_gate.py
    python3 -m pytest tests/ -q
    python3 integration/e2e/test_full_stack_diagnostic.py

## Contract changes

- [ ] No schema changed
- [ ] Schema changed, $id bumped, consumers updated

## Component API changes

- [ ] No public symbols changed
- [ ] Public symbols changed, component.json version bumped, CHANGELOG updated
