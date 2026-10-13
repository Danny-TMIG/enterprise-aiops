# platform

Source package for `platform`.

## Files

- `__init__.py`
- `platform.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Platform` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from platform import Platform
    eng = Platform()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
