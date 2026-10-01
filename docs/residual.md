# Grounding every module in the Residual Register

Every module in `app/` anchors to one or more entries in
"The Complete Residual Register — All Known to Man."

The anchor is a list of residual IDs the module terminates at.
The terminal residual is Ω. A module with no valid anchor is
unfaithful and must not be used.

## The anchor contract

    anchors(module) ⊆ {T-01 … Ω}

The chain:

    module → [ID₁, ID₂, …] → Ω

## Why this matters

Our modules do not invent residuals. They inherit them from the
register. `dissolve` carries `Z-01 (Meaning)`, not a homemade
notion of residue. `combinator` terminates at `M-04 (Halting)`,
not at "well the reducer runs." Every residue in our code is a
named entry in the register, addressable by ID.

## Validation

`validate()` returns OK only if every anchor ID is in the
register. If any module anchors to an ID not in the register,
the register is incomplete for our work and the missing ID must
be added or the module changed.

## The register's own residual

The register declares its own incompleteness (`C-B4`).
Our anchor map inherits the same residual: the anchors are
complete up to the modules we have written. New modules require
new anchors, and the act of adding them is Ω.
