# 95_OPERATIONS

Source package for `95_OPERATIONS`.

## Files

- `__init__.py`
- `95_OPERATIONS.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `95Operations` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 95_OPERATIONS import 95Operations
    eng = 95Operations()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
