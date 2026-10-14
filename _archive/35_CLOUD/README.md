# 35_CLOUD

Source package for `35_CLOUD`.

## Files

- `__init__.py`
- `35_CLOUD.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `35Cloud` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 35_CLOUD import 35Cloud
    eng = 35Cloud()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
