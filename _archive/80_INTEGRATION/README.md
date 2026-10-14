# 80_INTEGRATION

Source package for `80_INTEGRATION`.

## Files

- `__init__.py`
- `80_INTEGRATION.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `80Integration` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 80_INTEGRATION import 80Integration
    eng = 80Integration()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
