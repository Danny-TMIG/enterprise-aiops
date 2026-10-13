# data

Source package for `data`.

## Files

- `__init__.py`
- `data.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Data` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from data import Data
    eng = Data()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
