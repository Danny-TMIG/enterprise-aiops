# universal_platform

Legacy platform package. Superseded by aiops_platform for new work.
Kept for backwards compatibility with existing callers.

## Status

Maintenance-only. No new features. Bug fixes only.

## Migration

Replace imports of `universal_platform.*` with `aiops_platform.*` where
an equivalent module exists. See docs/architecture.md for the mapping.

## Layout

    universal_platform/
      __init__.py
      <subpackages>

## Note

Do not rename to `platform`. That name is reserved by the Python stdlib
and would shadow it for any process running from this repo root.
