# audit

Source package for `audit`.

## Files

- `__init__.py`
- `audit.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Audit` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from audit import Audit
    eng = Audit()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
