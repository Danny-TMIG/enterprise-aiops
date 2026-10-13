# slo

Source package for `slo`.

## Files

- `__init__.py`
- `slo.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Slo` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from slo import Slo
    eng = Slo()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
