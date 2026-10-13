# 01_BASELINE

Source package for `01_BASELINE`.

## Files

- `__init__.py`
- `01_BASELINE.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `01Baseline` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 01_BASELINE import 01Baseline
    eng = 01Baseline()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
