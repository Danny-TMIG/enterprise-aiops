# catalog/requirements/

## What is here

| File | Purpose |
|---|---|
| `requirements-map.json` | Machine-readable map from requirement ID to owning component |

## Content

`requirements-map.json` is generated from the nine requirement entries in
each component's `docs/requirements.md` (files `*-FR-01` through
`*-FR-09`). It is consumed by the conformance auditor. It should never be
hand-edited; regenerate it with the component docs as the source of truth.

## Current state

`requirements-map.json` is present with `"status": "draft"` and an empty
`requirements` list. Once component requirement docs are populated with
real content (not `TBD`), regenerate this map. Until then, the map
correctly reports that no requirements are registered.

## What does not belong here

Component-level requirement text. That lives in each component's
`docs/requirements.md`. This directory holds only the aggregated index.
