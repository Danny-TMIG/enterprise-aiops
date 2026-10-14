# catalog/

## What is here

Machine-readable registries that describe what exists in the repository.

| Path | Purpose |
|---|---|
| `inventories/components.json` | Component identity, layer, family, release scope |
| `inventories/modules.json` | Module-level index (one record per module) |
| `requirements/requirements-map.json` | Requirement ID → owning component |
| `deployment-map.json` | Deployment profile → component set |
| `release-scope.json` | What is in Core v1, deferred, gated, or quarantined |

## Rules

Everything in this directory is **generated**, not hand-edited. Source of
truth is the tree itself plus each component's `component.json` and
`docs/requirements.md`. Regenerate after any component change.

Drift between `catalog/` and the tree is a bug. `tooling/validation/status.py`
compares component counts as one check.

## What does not belong here

Documentation, prose, or diagrams. Those belong under `docs/`.
