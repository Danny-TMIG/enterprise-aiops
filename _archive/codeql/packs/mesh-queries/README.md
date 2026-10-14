# mesh-queries

Source package for `mesh-queries`.

## Files

- `__init__.py`
- `mesh_queries.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `MeshQueries` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from mesh_queries import MeshQueries
    eng = MeshQueries()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
