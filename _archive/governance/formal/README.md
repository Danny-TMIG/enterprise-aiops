# formal

Source package for `formal`.

## Files

- `__init__.py`
- `formal.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Formal` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from formal import Formal
    eng = Formal()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
