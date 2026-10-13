# symbol_atlas

Source package for `symbol_atlas`.

## Files

- `__init__.py`
- `symbol_atlas.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `SymbolAtlas` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from symbol_atlas import SymbolAtlas
    eng = SymbolAtlas()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
