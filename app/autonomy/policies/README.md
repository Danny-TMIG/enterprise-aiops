# policies

Source package for `policies`.

## Files

- `__init__.py`
- `policies.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Policies` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from policies import Policies
    eng = Policies()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
