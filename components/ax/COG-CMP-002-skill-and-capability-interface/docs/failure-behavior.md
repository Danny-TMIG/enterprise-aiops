# COG-CMP-002-skill-and-capability-interface — Failure Behavior

## Failure classes

| Class | Example | Required response |
|---|---|---|
| Input | malformed, injection, missing provenance | Reject |
| State | stale base, conflict, corruption | Stop, quarantine, escalate |
| Dependency | upstream unavailable | Fail closed |
| Evidence | missing, inconsistent | Mark incomplete |

## Fail-closed

Missing identity, authority, policy, classification, integrity, or
evidence dependencies must produce rejection, never partial application.
