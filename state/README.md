# state

Source package for `state`.

## Files

- `__init__.py`
- `state.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `State` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from state import State
    eng = State()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
