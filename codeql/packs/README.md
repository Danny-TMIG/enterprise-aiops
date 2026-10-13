# packs

Source package for `packs`.

## Files

- `__init__.py`
- `packs.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Packs` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from packs import Packs
    eng = Packs()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
