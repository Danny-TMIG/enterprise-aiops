# mlx_bridge

Source package for `mlx_bridge`.

## Files

- `__init__.py`
- `mlx_bridge.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `MlxBridge` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from mlx_bridge import MlxBridge
    eng = MlxBridge()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
