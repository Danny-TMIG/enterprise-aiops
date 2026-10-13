# nexus_bridge

Source package for `nexus_bridge`.

## Files

- `__init__.py`
- `nexus_bridge.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `NexusBridge` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from nexus_bridge import NexusBridge
    eng = NexusBridge()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
