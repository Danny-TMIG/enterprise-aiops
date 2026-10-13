# queries

Source package for `queries`.

## Files

- `__init__.py`
- `queries.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Queries` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from queries import Queries
    eng = Queries()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
