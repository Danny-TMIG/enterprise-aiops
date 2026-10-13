# sbom

Source package for `sbom`.

## Files

- `__init__.py`
- `sbom.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Sbom` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from sbom import Sbom
    eng = Sbom()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
