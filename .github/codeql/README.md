# codeql

Source package for `codeql`.

## Files

- `__init__.py`
- `codeql.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Codeql` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from codeql import Codeql
    eng = Codeql()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
