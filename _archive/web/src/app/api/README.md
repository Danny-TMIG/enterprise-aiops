# api

Source package for `api`.

## Files

- `__init__.py`
- `api.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Api` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from api import Api
    eng = Api()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
