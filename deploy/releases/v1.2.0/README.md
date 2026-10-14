# deploy/releases/v1.2.0/

## What is here

| File | Purpose |
|---|---|
| `manifest.json` | Release manifest for v1.2.0 |

## Manifest contents

The manifest records:

- Release version and status
- The HEAD commit the release was cut from
- The Python version used to build
- The lockfile SHA-256 hash for reproducibility
- The Omega Seal from the orchestrator run at release time
- The components included
- The open architecture decisions at release time
- The issue date

## Rules

Append-only. Once a release directory is committed, its manifest is never
edited. A new release goes in a new directory.

## Current state

`manifest.json` is present with `"status": "draft"`. All fields that would
pin the release (`head_commit`, `lockfile_sha256`, `omega_seal`,
`issued_at`) are `null`. This directory represents the **shape** of a
release, not a cut release. No release has been tagged.
