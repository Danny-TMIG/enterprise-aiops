# metrics

Source package for `metrics`.

## Files

- `__init__.py`
- `metrics.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Metrics` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from metrics import Metrics
    eng = Metrics()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
