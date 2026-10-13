# pen

Source package for `pen`.

## Files

- `__init__.py`
- `pen.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Pen` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from pen import Pen
    eng = Pen()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
