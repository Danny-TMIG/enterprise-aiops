# conformance

Source package for `conformance`.

## Files

- `__init__.py`
- `conformance.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Conformance` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from conformance import Conformance
    eng = Conformance()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
