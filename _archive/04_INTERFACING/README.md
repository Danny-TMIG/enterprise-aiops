# 04_INTERFACING

Source package for `04_INTERFACING`.

## Files

- `__init__.py`
- `04_INTERFACING.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `04Interfacing` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 04_INTERFACING import 04Interfacing
    eng = 04Interfacing()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
