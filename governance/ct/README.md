# ct

Source package for `ct`.

## Files

- `__init__.py`
- `ct.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Ct` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from ct import Ct
    eng = Ct()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
