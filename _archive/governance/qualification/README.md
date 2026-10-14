# qualification

Source package for `qualification`.

## Files

- `__init__.py`
- `qualification.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Qualification` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from qualification import Qualification
    eng = Qualification()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
