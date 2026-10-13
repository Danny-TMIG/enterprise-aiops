---- MODULE license_compliance ----
EXTENDS Naturals
CONSTANTS Packages, Compatible
VARIABLES licenses, audit
Init == licenses = [p \in Packages |-> "UNKNOWN"] /\ audit = {}
Audit(p) == licenses[p] = "UNKNOWN" /\ licenses' = [licenses EXCEPT ![p] = "AUDITED"] /\ audit' = audit \cup {p}
Mark(p) == licenses[p] = "AUDITED" /\ licenses' = [licenses EXCEPT ![p] = IF p \in Compatible THEN "OK" ELSE "VIOLATION"]
Safety == \A p \in Packages : licenses[p] \in {"UNKNOWN","AUDITED","OK","VIOLATION"}
Next == \E p \in Packages : Audit(p) \/ Mark(p)
====
