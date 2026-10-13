# sovereign-bounded-matrix

Source package for `sovereign-bounded-matrix`.

## Files

- `__init__.py`
- `sovereign_bounded_matrix.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `SovereignBoundedMatrix` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from sovereign_bounded_matrix import SovereignBoundedMatrix
    eng = SovereignBoundedMatrix()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
