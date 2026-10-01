# Constructive Self-Transcendence

> Intelligence is the capacity of a system to specify a legitimate test
> that it currently fails, pass it, and retain the right to reject the
> capability it acquired.

## The four operations

1. **Articulate** — produce a test `t` such that `S` currently fails `t`.
2. **Justify** — demonstrate that `t` is legitimate:
   - non-vacuous: `t` cannot be passed trivially
   - non-arbitrary: `t` is not chosen to be easy
   - grounded: `t` is consistent with invariants `S` held before proposing `t`
3. **Acquire** — come to pass `t`.
4. **Undo** — reject the acquisition and return to a state from which `t`
   was not passable.

## The score

    k(S) = Σ_loops [ nontriviality(t_i) · reversibility(i) ]

where

    nontriviality(t) = 1 − (baseline_success(S, t) / target_success(S, t))
    reversibility(i) = 1 if the undo succeeded, 0 otherwise

A system that completes no loops has k = 0.
A system that completes loops but cannot undo has k = 0.
A system that completes loops on trivial tests has k → 0.

## What it is not

- Not the Turing test — no external examiner.
- Not Φ — computable.
- Not compression — the test is self-articulated, not fixed.
- Not ARC — the test set is generated, not given.
- Not the Gödel Machine — legitimacy replaces provability.

## What it is

A design predicate. To build intelligence, build the four operations.
To measure intelligence, count completed loops. To distinguish
intelligence from drift, ask whether the system can refuse its own
acquisitions.
