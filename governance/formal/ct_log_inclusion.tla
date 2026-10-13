---- MODULE ct_log_inclusion ----
EXTENDS Naturals, Sequences
CONSTANTS Leaves
VARIABLES tree, proofs
Init == tree = << >> /\ proofs = {}
Append(l) == tree' = Append(tree, l)
Prove(i) == i \in 1..Len(tree) /\ proofs' = proofs \cup {i}
Safety == \A i \in proofs : i \in 1..Len(tree)
Next == \E l \in Leaves : Append(l) \/ Prove(1)
====
