# whisper_cpp_bindings

Source package for `whisper_cpp_bindings`.

## Files

- `__init__.py`
- `whisper_cpp_bindings.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `WhisperCppBindings` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from whisper_cpp_bindings import WhisperCppBindings
    eng = WhisperCppBindings()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
