# change

Source package for `change`.

## Files

- `__init__.py`
- `change.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Change` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from change import Change
    eng = Change()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
