# dsl

Source package for `dsl`.

## Files

- `__init__.py`
- `dsl.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Dsl` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from dsl import Dsl
    eng = Dsl()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
