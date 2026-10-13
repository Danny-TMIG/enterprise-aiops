# certificates

Source package for `certificates`.

## Files

- `__init__.py`
- `certificates.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Certificates` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from certificates import Certificates
    eng = Certificates()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
