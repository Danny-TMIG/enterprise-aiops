# ingress

Source package for `ingress`.

## Files

- `__init__.py`
- `ingress.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Ingress` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from ingress import Ingress
    eng = Ingress()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
