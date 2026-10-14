# tooling/release/

## What is here

Scripts that produce release artifacts.

## What belongs here

- Scripts that build the release manifest
- Scripts that tag the release commit
- Scripts that publish artifacts

## Rules

- **Callable from CI and from a developer workstation.** Same behavior
  either way.
- **No release policy.** These scripts execute a release; they do not
  decide what gets released. That is a human decision recorded in the
  manifest.
- **Reproducible.** Same commit + same inputs = same release artifacts.

## Current state

Empty. No release scripts have been authored. No version has been tagged.
