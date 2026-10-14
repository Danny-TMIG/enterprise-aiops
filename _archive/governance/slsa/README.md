# slsa

Source package for `slsa`.

## Files

- `__init__.py`
- `slsa.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Slsa` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from slsa import Slsa
    eng = Slsa()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
