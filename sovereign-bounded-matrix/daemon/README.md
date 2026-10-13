# daemon

Source package for `daemon`.

## Files

- `__init__.py`
- `daemon.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Daemon` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from daemon import Daemon
    eng = Daemon()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
