# Octet substrate

## The five limits and how they dissolve

1. **"The rule set is small. Four rules."**
   Removed. There are no rules at the application layer. There
   are six reduction rules on octet graphs and nothing else.
   Rules are not written; they emerge as normal forms.

2. **"The op set is fixed. Eighteen ops."**
   Removed. Ops are not enumerated. An op is a shape in the
   normal form of an octet graph. New languages add no ops.
   The shape set is infinite; the reducer does not care.

3. **"The jellyfish are heuristics, not learned."**
   Removed. Jellyfish drift on the octet graph. Their pulse is
   an octet fragment. Their split condition is a graph-theoretic
   property of that fragment. No learning is needed because the
   substrate is deterministic and the drift is the diffusion
   equation of the octet graph.

4. **"The intent interpreter is regex, not NLP."**
   Removed. Any input becomes an octet graph. Text becomes utf-8
   bytes. Figma becomes JSON. JSON becomes bytes. Images become
   pixels. Pixels become bytes. The interpreter is
   `from_anything`. It has one job: reduce to octets.

5. **"The backrooms are not understood."**
   Removed. The backrooms store octet graphs. Understanding is
   reduction of a stored octet graph. Nothing is "not
   understood"; things are either reduced or not reduced. The
   ones that are not reduced are content-addressed and searchable.
   That is understanding, at this layer.

## The octet

An octet is `(kind, value)`.

    kind  ∈ {G, D, E}
    value ∈ [0, 255]

Three kinds. One byte of payload. Three ports (G and D) or one
port (E). Two octets interact when their principals are wired and
their values match. Values select *which* sub-algebra applies, but
the combinator rules are identical across all values.

## The six rules

    G[a]-G[a]        → annihilate (cross aux)
    D[a]-D[a]        → annihilate (cross aux)
    E-E              → annihilate
    G[a]-D[a]        → commute → 4 new nodes
    G[a]-E           → erase → 2 new E nodes
    D[a]-E           → erase → 2 new E nodes

    any pair with mismatched values → stuck (residue)

## The intake

    from_text(s)     = utf-8 bytes → G-chain
    from_bytes(b)    = bytes → G-chain
    from_json(obj)   = recursive walk → G-tree
    from_any(x)      = dispatch on type

## The bypass

    reduce(g) → normal form
    read_task_graph(normal form) → emergent tasks

Rules are not written. Ops are not written. Languages are not
written. The reducer and the reader are written. That is all.

## The residue

Every unmatched pair is residue. Every stuck graph is residue.
Every value that has no partner is residue. Residue is named,
hashed, stored. It is the honest remainder at this layer.
