# ncf_layer

Source package for `ncf_layer`.

## Files

- `__init__.py`
- `ncf_layer.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `NcfLayer` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from ncf_layer import NcfLayer
    eng = NcfLayer()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
