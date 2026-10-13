# proof

Source package for `proof`.

## Files

- `__init__.py`
- `proof.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Proof` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from proof import Proof
    eng = Proof()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
