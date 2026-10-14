# libraries/crypto/

## What is here

| File | Purpose |
|---|---|
| `sovereign_crypto.py` | Shared cryptographic primitives |

## What belongs here

Hashing, signing, key derivation, and similar operations used across
layers. Supports the Common Envelope integrity field, the Omega Seal
computation, and any signature verification in the evidence path.

## Rules

- **Wrap, do not implement.** This library wraps well-reviewed libraries.
  A hand-rolled cipher is a bug regardless of how correct it looks.
- **Narrow interface.** Sign, verify, hash, derive. Nothing more.
- **No policy.** This library does not decide when to sign or what to sign.
  That is component policy.
- **Test vectors.** Every primitive it wraps is tested against published
  test vectors, so a change in the underlying library is caught immediately.
- **No component dependencies.** Components import this library; not the
  reverse.

## Why this matters

This is one of two libraries where a bug is catastrophic. Its review
requirements should be the strictest in the repository.
