---- MODULE rogue_detection ----
EXTENDS Naturals, TLC
CONSTANTS Processes
VARIABLES state, detection
Init == state = [p \in Processes |-> "UNKNOWN"] /\ detection = {}
Detect(p) == state[p] = "UNKNOWN" /\ state' = [state EXCEPT ![p] = "TRUE"] /\ detection' = detection \cup {p}
Safety == \A p \in Processes : state[p] \in {"UNKNOWN","TRUE","FALSE","CONFLICT"}
Next == \E p \in Processes : Detect(p)
====
