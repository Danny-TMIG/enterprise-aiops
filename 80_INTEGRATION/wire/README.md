# wire

Source package for `wire`.

## Files

- `__init__.py`
- `wire.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Wire` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from wire import Wire
    eng = Wire()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
