# registry

Source package for `registry`.

## Files

- `__init__.py`
- `registry.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Registry` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from registry import Registry
    eng = Registry()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
