# threat

Source package for `threat`.

## Files

- `__init__.py`
- `threat.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Threat` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from threat import Threat
    eng = Threat()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
