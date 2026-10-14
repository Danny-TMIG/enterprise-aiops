# contracts/apis/

## What is here

Interface definitions for the operations that accept and return boundary
objects. Examples: OpenAPI specifications, gRPC proto files, or equivalent.

## What belongs here

Every API definition in this directory must:

1. Name the boundary object it carries.
2. Declare the direction of the call (which layer initiates).
3. Reference the canonical schema for the object from
   `contracts/canonical/` or `40_CROSS_STACK_INTEGRATION/05_Canonical_Schemas/`.
4. State the failure semantics — what the caller sees when the operation
   fails closed.

## Current state

Empty. No API definitions have been authored. The transport decision
(`GOV-DEC-001` / `CMP-DEC-001`) is Open; the API layer cannot be finalized
until that decision closes.

## What does not belong here

Implementation code, schema definitions, or test fixtures.
