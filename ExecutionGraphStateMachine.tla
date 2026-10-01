---------------- MODULE ExecutionGraphStateMachine ----------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS Nodes, MaxRequests

VARIABLES node_states, request_queue, active_inference

vars == <<node_states, request_queue, active_inference>>

Init == 
    /\ node_states = [n \in Nodes |-> "IDLE"]
    /\ request_queue = <<>>
    /\ active_inference = FALSE

DispatchRequest == 
    /\ active_inference = FALSE
    /\ active_inference' = TRUE
    /\ UNCHANGED <<node_states, request_queue>>

CompleteInference == 
    /\ active_inference = TRUE
    /\ active_inference' = FALSE
    /\ UNCHANGED <<node_states, request_queue>>

Next == 
    \/ DispatchRequest
    \/ CompleteInference

Spec == Init /\ [][Next]_vars

--FAIRNESS SF_vars(Next)

(* Safety Invariant: Never allow concurrent inference executions on single unified memory instance *)
SafetyMutex == active_inference => (EXISTS n \in Nodes : node_states[n] \in {"PROCESSING", "IDLE"})

=============================================================================
