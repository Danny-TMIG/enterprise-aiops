# license

Source package for `license`.

## Files

- `__init__.py`
- `license.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `License` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from license import License
    eng = License()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
