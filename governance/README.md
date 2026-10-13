# governance

Source package for `governance`.

## Files

- `__init__.py`
- `governance.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Governance` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from governance import Governance
    eng = Governance()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
