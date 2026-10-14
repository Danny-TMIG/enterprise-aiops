# verifiers

Source package for `verifiers`.

## Files

- `__init__.py`
- `verifiers.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Verifiers` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from verifiers import Verifiers
    eng = Verifiers()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
