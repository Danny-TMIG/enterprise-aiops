# COG-CMP-005-adaptation-manager — State Model

## State

- What state does this component own?
- What state does it merely read?
- What is transient vs. durable?

## Transitions

Each transition should name the trigger, precondition, and postcondition.
Silent last-write-wins is prohibited for durable state.

## Versioning

Every state version identifies its predecessor or merge set, operation,
issuer, time, provenance, and evidence.
