# coherence

Source package for `coherence`.

## Files

- `__init__.py`
- `coherence.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Coherence` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from coherence import Coherence
    eng = Coherence()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
