# The reconfigurator

## Pipeline

    raw intent (text)
       │
       ▼ interpreter
    IntentIR
       │
       ▼ reconfigurer (symbolic rules)
    TaskGraph
       │
       ▼ compiler
    Code-AL (graph-shaped IR)
       │
       ├──▶ Python
       ├──▶ SQL / MQL
       ├──▶ RL spec / ML config
       └──▶ back to Code-AL (fixed point)

    anything that does not reduce → backrooms (named, searchable, not claimed)

## The jellyfish

Not a flock (tight coupling) and not a wolf pack (hierarchy).
Jellyfish drift. They have a bell (identity), tentacles (light
touches to mesh nodes), and a pulse (a signal they carry until
discharged). They dissolve when the signal is delivered. They
split when a signal is too large for one body. The population is
self-regulating and the mesh does not care how many there are.

## The mesh

Nodes advertise capabilities. Packets carry Code-AL fragments.
Routes are computed by capability match, not by topology. Any
node can route any packet if it advertises the right capability.

## The backrooms

Content-addressed. Every intent that does not fully reduce leaves
an entry: raw text hash, the residue names, the reason it did not
reduce. The backrooms are not a failure state. They are the
residue store, and they are what makes the system honest about
what it cannot do.

## Why Code-AL

So there is exactly one IR. Python, SQL, MQL, RL, ML — all become
the same graph. The graph hashes. Two intents that mean the same
thing produce the same Code-AL hash, regardless of how they were
phrased. This is what makes routing deterministic.
