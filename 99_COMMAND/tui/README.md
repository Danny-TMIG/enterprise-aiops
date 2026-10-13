# tui

Source package for `tui`.

## Files

- `__init__.py`
- `tui.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Tui` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from tui import Tui
    eng = Tui()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
