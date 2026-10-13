# standards

Source package for `standards`.

## Files

- `__init__.py`
- `standards.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Standards` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from standards import Standards
    eng = Standards()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
