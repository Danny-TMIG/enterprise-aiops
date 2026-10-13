# clickhouse_config

Source package for `clickhouse_config`.

## Files

- `__init__.py`
- `clickhouse_config.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `ClickhouseConfig` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from clickhouse_config import ClickhouseConfig
    eng = ClickhouseConfig()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
