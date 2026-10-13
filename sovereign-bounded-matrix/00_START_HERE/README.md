# 00_START_HERE

Source package for `00_START_HERE`.

## Files

- `__init__.py`
- `00_START_HERE.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `00StartHere` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 00_START_HERE import 00StartHere
    eng = 00StartHere()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
