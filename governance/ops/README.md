# ops

Source package for `ops`.

## Files

- `__init__.py`
- `ops.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Ops` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from ops import Ops
    eng = Ops()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
