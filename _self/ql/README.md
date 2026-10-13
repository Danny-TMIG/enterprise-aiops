# ql

Source package for `ql`.

## Files

- `__init__.py`
- `ql.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Ql` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from ql import Ql
    eng = Ql()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
