# spec

Source package for `spec`.

## Files

- `__init__.py`
- `spec.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Spec` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from spec import Spec
    eng = Spec()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
