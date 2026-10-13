# grid

Source package for `grid`.

## Files

- `__init__.py`
- `grid.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Grid` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from grid import Grid
    eng = Grid()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
