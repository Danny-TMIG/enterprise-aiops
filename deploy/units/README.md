# deploy/units/

## What is here

Deployable units. Each unit is a concrete thing that runs — a process, a
container, a service — composed from one or more components.

## Current units

| Unit | Purpose |
|---|---|
| `core-runtime-unit/` | The minimal ASF unit |

## What belongs in a unit

- `unit.json` — identity, components included, profiles supported, external dependencies
- `build/` — reproducible build steps
- `config/` — configuration, no secrets
- `manifests/` — deployment manifests for the target platform
- `tests/` — unit-level tests (starts, healthy, accepts work, shuts down)
- `runbook.md` — operational runbook: start, health check, stop, failure handling

## Status

**Empty.** `core-runtime-unit` has the shape (directories, manifest schema,
runbook template) but no actual build, config, or manifests. The
architecture decisions that would fix a target platform are Open.
