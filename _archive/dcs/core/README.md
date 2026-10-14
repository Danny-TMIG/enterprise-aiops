# core

Source package for `core`.

## Files

- `__init__.py`
- `core.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Core` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from core import Core
    eng = Core()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
