# db

Source package for `db`.

## Files

- `__init__.py`
- `db.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Db` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from db import Db
    eng = Db()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
