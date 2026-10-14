# catalog/inventories/

## What is here

| File | Purpose |
|---|---|
| `components.json` | One record per logical component |
| `modules.json` | One record per module within a component |

## components.json

Keyed by component ID (e.g. `COG-INT-001`). Each record carries ID, slug,
layer, family, release scope, and path. This is the source of truth for
"what components exist" and "which release do they belong to."

## modules.json

Finer-grained than components.json: one record per module under
`components/*/*/src/`, keyed by component ID plus module name. Records
whether a module is public or internal, and its stability status.

## Generation

Regenerate from the tree:

    python3 tooling/validation/generate_spec_to_code.py

Do not hand-edit. A component added to the tree but absent from
`components.json` is invisible to tooling; a component listed here but
absent from the tree causes a TREE block failure in `status.py`.
