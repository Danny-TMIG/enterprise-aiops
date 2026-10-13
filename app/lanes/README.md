# lanes

Source package for `lanes`.

## Files

- `__init__.py`
- `lanes.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Lanes` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from lanes import Lanes
    eng = Lanes()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
