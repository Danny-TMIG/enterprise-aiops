# 20_GOVERNANCE

Source package for `20_GOVERNANCE`.

## Files

- `__init__.py`
- `20_GOVERNANCE.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `20Governance` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 20_GOVERNANCE import 20Governance
    eng = 20Governance()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
