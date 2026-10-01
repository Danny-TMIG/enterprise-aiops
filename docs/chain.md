# The Full Chain — distilled

## What the document establishes

36 roles. 12 phases. The chain is a single morphism in the
topos Skill. Composition is associative. Six adjunctions pair
roles as (produce, verify). Four residues remain after all 36
are composed: intent, resolver, chooser of chooser, successor
of successor. All four terminate at Ω.

## What our previous modules cover

| Role | Covered by |
|---|---|
| R02 | (none) |
| R04 | app.reconfig.interpreter |
| R07 | app.reconfig.rules |
| R10 | app.octet |
| R11 | app.reconfig.emit |
| R13 | app.dominion.search |
| R14 | app.dominion.search |
| R15 | (none) |
| R16 | app.nested.tower |
| R17 | app.cst.gate |
| R31 | app.agency.gate |
| R32 | app.agency.registry |
| R35 | app.agency.revoke |

## What this module supplies

- All 36 roles as typed records, executable where tractable.
- `compose(role_a, role_b)` with associativity check.
- The six adjunctions detected at runtime.
- Self-similarity: `apply_chain(role)` builds the chain that
  would build that role.
- Four terminal residues exposed as first-class objects, each
  anchored to Ω in the residual register.

## The arity contract

Each role declares its arity as the document specifies.
- Arity 0: terminal (intent).
- Arity 1: unary function.
- Arity 2: binary (spec, artifact) pairs.
- Arity N: collection.

Composition respects arity: a role consuming arity-k consumes
exactly k upstream witnesses; a role producing arity-k produces
k downstream witnesses.

## The witness contract

Every role's output is a Witness:

    Witness(id, kind, payload, verify: () -> Verdict, residue)

`verify()` is the role's own check. If it returns PASS, the
witness may be consumed downstream. If it returns FAIL, the
chain halts at that role and the residue is recorded.

## The residue of the chain

After running all 36 roles, four residues remain:

    intent        — R01's output is not derived
    resolver      — each role's name needs an external resolver
    chooser²      — R02 applied to R02
    successor²    — R36 applied to R36

Each is registered as a Residual in app.residual, terminating
at Ω.
