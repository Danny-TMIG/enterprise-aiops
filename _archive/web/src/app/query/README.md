# query

Source package for `query`.

## Files

- `__init__.py`
- `query.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Query` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from query import Query
    eng = Query()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
