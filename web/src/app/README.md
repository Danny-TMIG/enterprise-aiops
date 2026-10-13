# app

Source package for `app`.

## Files

- `__init__.py`
- `app.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `App` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from app import App
    eng = App()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
