# supervisor

Source package for `supervisor`.

## Files

- `__init__.py`
- `supervisor.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Supervisor` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from supervisor import Supervisor
    eng = Supervisor()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
