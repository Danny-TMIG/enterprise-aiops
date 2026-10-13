# _self

Source package for `_self`.

## Files

- `__init__.py`
- `_self.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Self` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from _self import Self
    eng = Self()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
