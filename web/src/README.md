# src

Source package for `src`.

## Files

- `__init__.py`
- `src.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Src` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from src import Src
    eng = Src()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
