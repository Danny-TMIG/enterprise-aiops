# health

Source package for `health`.

## Files

- `__init__.py`
- `health.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Health` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from health import Health
    eng = Health()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
