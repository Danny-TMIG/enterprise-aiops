# meta_glasses_integration

Source package for `meta_glasses_integration`.

## Files

- `__init__.py`
- `meta_glasses_integration.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `MetaGlassesIntegration` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from meta_glasses_integration import MetaGlassesIntegration
    eng = MetaGlassesIntegration()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
