# evidence

Source package for `evidence`.

## Files

- `__init__.py`
- `evidence.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Evidence` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from evidence import Evidence
    eng = Evidence()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
