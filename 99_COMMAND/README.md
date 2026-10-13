# 99_COMMAND

Source package for `99_COMMAND`.

## Files

- `__init__.py`
- `99_COMMAND.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `99Command` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 99_COMMAND import 99Command
    eng = 99Command()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
