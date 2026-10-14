# pilot

Source package for `pilot`.

## Files

- `__init__.py`
- `pilot.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Pilot` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from pilot import Pilot
    eng = Pilot()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
