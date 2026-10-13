# vatican

Source package for `vatican`.

## Files

- `__init__.py`
- `vatican.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Vatican` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from vatican import Vatican
    eng = Vatican()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
