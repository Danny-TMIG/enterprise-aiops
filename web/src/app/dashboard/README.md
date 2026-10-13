# dashboard

Source package for `dashboard`.

## Files

- `__init__.py`
- `dashboard.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Dashboard` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from dashboard import Dashboard
    eng = Dashboard()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
