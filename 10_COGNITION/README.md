# 10_COGNITION

Source package for `10_COGNITION`.

## Files

- `__init__.py`
- `10_COGNITION.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `10Cognition` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 10_COGNITION import 10Cognition
    eng = 10Cognition()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
