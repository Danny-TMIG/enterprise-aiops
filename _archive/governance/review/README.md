# review

Source package for `review`.

## Files

- `__init__.py`
- `review.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `Review` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from review import Review
    eng = Review()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
