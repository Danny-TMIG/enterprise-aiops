# migrations

Source package for `migrations`.

## Files

- `__init__.py`
- `migrations.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Migrations` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from migrations import Migrations
    eng = Migrations()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
