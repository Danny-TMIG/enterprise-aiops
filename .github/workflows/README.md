# workflows

Source package for `workflows`.

## Files

- `__init__.py`
- `workflows.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Workflows` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from workflows import Workflows
    eng = Workflows()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
