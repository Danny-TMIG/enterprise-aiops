# auto_app

Source package for `auto_app`.

## Files

- `__init__.py`
- `auto_app.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `AutoApp` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from auto_app import AutoApp
    eng = AutoApp()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
