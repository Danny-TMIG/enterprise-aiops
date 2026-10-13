# pimeyes_integration

Source package for `pimeyes_integration`.

## Files

- `__init__.py`
- `pimeyes_integration.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `PimeyesIntegration` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from pimeyes_integration import PimeyesIntegration
    eng = PimeyesIntegration()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
