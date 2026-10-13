# components

Source package for `components`.

## Files

- `__init__.py`
- `components.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Components` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from components import Components
    eng = Components()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
