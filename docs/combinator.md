# Interaction Combinators as the substrate

## What is removed

- LLM as generator.  No prompt, no cache, no canonicalization.
- KV cache.         No history, no attention over sequence.
- GPU / CUDA / matmul / softmax / backprop.

## What is added

Three node kinds:  γ (constructor)  δ (duplicator)  ε (eraser).
Six reduction rules.  All local.  All deterministic.

## The attention substitute

In a transformer, attention is a learned weighting over all positions.
Here, "attention" is the set of *active pairs* — pairs of nodes whose
principal ports are wired. Each reduction step touches exactly two
nodes and produces at most four. Sparsity is structural, not learned.

## The cache substitute

There is no cache. The graph at step n determines step n+1 exactly.
The local working set of any single reduction is 6 ports. The global
state is the graph, and it can be externalized between steps — hence
"no RAM residency required."

## The fixed point

The normal form is unique (confluence). Its content hash is the answer.
Two programs with the same normal form have the same hash. No
canonicalization of the input is required because the normal form is
already canonical.

## The hardware lottery

The six rules are a state machine. Any substrate that can rewrite a
graph can run them: CPU, GPU, FPGA, ASIC, memristor crossbar, cellular
automaton, pencil. There is no matmul, no CUDA, no torch. The same
program runs unchanged on every substrate.

## The logic monopoly

The primitive is not a float. It is a node with three ports and three
kinds. NAND is derived from the encoding, not assumed. The system's
"logic" is the reduction relation itself. No gradients anywhere.

## The residue

The residue that the taste tower carried — voice, rhythm, the residue
of the checkable class — is unchanged. Interaction combinators
reduce what is expressible in their grammar. Whatever is not
expressible is the residue. It is named, never discharged.
