# asm

Source package for `asm`.

## Files

- `__init__.py`
- `asm.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Asm` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from asm import Asm
    eng = Asm()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
