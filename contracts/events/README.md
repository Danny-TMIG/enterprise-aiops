# contracts/events/

## What is here

Asynchronous event definitions — the payloads published and subscribed
between components.

## What belongs here

Every event definition must:

1. Name the emitting component.
2. Reference the payload schema.
3. Declare the delivery guarantee (at-most-once, at-least-once,
   exactly-once).
4. State whether the event is idempotent.

**Cancellation and revocation directives are the critical events.** The
FAS requires them to be observable state transitions, not ordinary
failures. Any event that carries an authority grant without a
corresponding `AuthorizationDecision` is a bug.

## Current state

Empty. No event definitions have been authored.

## What does not belong here

Synchronous request-response contracts. Those belong in `contracts/apis/`.
