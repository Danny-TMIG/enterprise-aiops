# stream

Source package for `stream`.

## Files

- `__init__.py`
- `stream.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Stream` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from stream import Stream
    eng = Stream()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
