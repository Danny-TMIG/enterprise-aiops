# lib

Source package for `lib`.

## Files

- `__init__.py`
- `lib.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Lib` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from lib import Lib
    eng = Lib()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
