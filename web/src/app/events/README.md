# events

Source package for `events`.

## Files

- `__init__.py`
- `events.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Events` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from events import Events
    eng = Events()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
