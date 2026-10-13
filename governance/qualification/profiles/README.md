# profiles

Source package for `profiles`.

## Files

- `__init__.py`
- `profiles.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Profiles` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from profiles import Profiles
    eng = Profiles()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
