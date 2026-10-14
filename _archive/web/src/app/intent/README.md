# intent

Source package for `intent`.

## Files

- `__init__.py`
- `intent.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Intent` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from intent import Intent
    eng = Intent()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
