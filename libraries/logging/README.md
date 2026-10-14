# libraries/logging/

## What is here

Shared structured logging and telemetry.

## What belongs here

A single structured logger used by every component, plus helpers for
correlation and causation IDs drawn from the Common Envelope.

## Why this matters

The evidence path depends on the ability to reconstruct what happened and
in what order. Every log entry should carry correlation and causation IDs
so a reader can reconstruct a decision chain from logs alone.

## Rules

- The library must not decide what to log or at what level. That is
  component policy.
- This is the only place in the repository that writes directly to stdout
  or stderr outside of tooling. Centralizing makes redaction, formatting,
  and routing possible without touching every component.
- Fast enough that logging never becomes a bottleneck in the execution
  path. Safe to call from any thread.

## Current state

Empty. No shared logger has been factored out yet.
