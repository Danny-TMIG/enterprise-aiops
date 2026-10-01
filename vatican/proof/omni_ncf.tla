---------------------------- MODULE omni_ncf ----------------------------
EXTENDS Integers, Sequences, FiniteSets

CONSTANTS Nodes, MaxEpoch

VARIABLES state, locked, verified_corpus, epoch

vars == <<state, locked, verified_corpus, epoch>>

Init == 
    /\ state = "Idle"
    /\ locked = FALSE
    /\ verified_corpus = FALSE
    /\ epoch = 0

AcquireLock ==
    /\ state = "Idle"
    /\ ~locked
    /\ locked' = TRUE
    /\ state' = "Locked"
    /\ UNCHANGED <<verified_corpus, epoch>>

VerifyCorpus ==
    /\ state = "Locked"
    /\ ~verified_corpus
    /\ verified_corpus' = TRUE
    /\ state' = "Verified"
    /\ UNCHANGED <<locked, epoch>>

SyncConsensus ==
    /\ state = "Verified"
    /\ epoch < MaxEpoch
    /\ epoch' = epoch + 1
    /\ locked' = FALSE
    /\ verified_corpus' = FALSE
    /\ state' = "Idle"

Next == 
    \/ AcquireLock
    \/ VerifyCorpus
    \/ SyncConsensus

Spec == Init /\ [][Next]_vars

* Invariants
SafetyInvariant == (state = "Verified") => locked
EpochBound == epoch <= MaxEpoch

=============================================================================
