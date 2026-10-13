# manifests

Source package for `manifests`.

## Files

- `__init__.py`
- `manifests.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Manifests` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from manifests import Manifests
    eng = Manifests()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
