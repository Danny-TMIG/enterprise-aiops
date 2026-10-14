# compliance

Source package for `compliance`.

## Files

- `__init__.py`
- `compliance.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Compliance` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from compliance import Compliance
    eng = Compliance()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
