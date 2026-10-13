# mark

Source package for `mark`.

## Files

- `__init__.py`
- `mark.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Mark` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from mark import Mark
    eng = Mark()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
