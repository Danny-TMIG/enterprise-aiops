# dis

Source package for `dis`.

## Files

- `__init__.py`
- `dis.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Dis` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from dis import Dis
    eng = Dis()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
