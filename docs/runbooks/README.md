# runbooks

Source package for `runbooks`.

## Files

- `__init__.py`
- `runbooks.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Runbooks` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from runbooks import Runbooks
    eng = Runbooks()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
