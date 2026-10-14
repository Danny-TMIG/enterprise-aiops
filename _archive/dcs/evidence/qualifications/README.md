# qualifications

Source package for `qualifications`.

## Files

- `__init__.py`
- `qualifications.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Qualifications` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from qualifications import Qualifications
    eng = Qualifications()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
