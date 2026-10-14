# ui

Source package for `ui`.

## Files

- `__init__.py`
- `ui.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Ui` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from ui import Ui
    eng = Ui()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
