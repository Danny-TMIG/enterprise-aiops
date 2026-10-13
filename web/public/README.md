# public

Source package for `public`.

## Files

- `__init__.py`
- `public.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Public` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from public import Public
    eng = Public()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
