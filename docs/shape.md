# The Shape of the System

```
THE SHAPE OF THE SYSTEM
==================================================================

Three adjunctions. One meta-anchor.
Everything else is implementation.

── Adjunction 1: Integration ⊣ Distribution ──
    L (left):   app.combinator.graph (the graph)
    R (right):  app.combinator.substrate (RAM / streaming / process)
    unit:       graph -> RAM(graph)
    counit:     reduce(substrate(graph)) -> normal_form(graph)
    witness:    The same six IC reduction rules produce the same normal form on RAMSubstrate and StreamingSubstrate. The graph is the source of truth; the substrate is a realization. Changing the substrate does not change the normal form.
    proof:      tests/test_slice.py::test_03_cd_nand_all_levels

── Adjunction 2: Distribution ⊣ Experience ──
    L (left):   app.train.core (39 tiles, 156 outcomes)
    R (right):  app.train.cd_state (one digest + one CD vector)
    unit:       39 tiles x 156 outcomes -> one CD element via resolve_cd
    counit:     one CD element -> the fields of a Run
    witness:    resolve_cd(run) compresses 39 per-tile coordinates into a single level-6 CD vector deterministically. The same Run always produces the same CD. The distribution is the 39 coordinates; the experience is the one element.
    proof:      tests/test_slice.py::test_02_parallel_grid

── Adjunction 3: Experience ⊣ Integration ──
    L (left):   app.reconfig.codeal (one IR)
    R (right):  app.reconfig.emit (Python, SQL, MQL, RL)
    unit:       intent -> Code-AL IR via interpret + apply_rules + from_tasks
    counit:     Code-AL IR -> four target languages via emit_all
    witness:    Two paraphrases that mean the same thing produce the same Code-AL hash. The IR is canonical because the rules are content-addressed and the emission is a pure function of the CAProgram. The experience (four languages out) and the integration (one IR in) are the same operation viewed from the two ends.
    proof:      tests/test_slice.py::test_01_intent_to_code

── Meta-anchor ──
    The residual register  (app.residual.terminate)
    residual: Ω
    rule:     Every module anchors to a specific residual ID. Every chain walks to Ω. A module whose anchor does not resolve is unfaithful and is rejected by app.residual.anchors.validate.

==================================================================
Everything else — every module, every test, every
registry, every document — is an implementation of
this shape. Renaming a file does not change the shape.
Moving a test does not change the shape. Deleting a
module does not change the shape. The shape is what
the system *is*, not what it is called.
==================================================================
```
