# mql

Source package for `mql`.

## Files

- `__init__.py`
- `mql.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Mql` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from mql import Mql
    eng = Mql()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
