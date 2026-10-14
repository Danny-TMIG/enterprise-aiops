# worker

Source package for `worker`.

## Files

- `__init__.py`
- `worker.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Worker` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from worker import Worker
    eng = Worker()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
