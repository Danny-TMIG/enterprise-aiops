# deploy/

## What is here

Everything needed to stand up ASF on physical infrastructure.

| Path | Purpose |
|---|---|
| `units/` | Deployable units — concrete things that run |
| `profiles/` | Deployment profiles — M, L, S, E, G |
| `releases/` | Release manifests, one directory per version |

## Status

**Nothing here runs yet.** Every directory below this one describes the
shape of a deployment, not a deployment that has been built. The
architecture-level decisions that would fix a physical shape
(`CMP-DEC-003`, `CMP-DEC-004`, `CMP-DEC-005`, `GOV-DEC-002`) are all Open.

## Deployment profiles

| Profile | Realization | v1 treatment |
|---|---|---|
| M | Mobile / constrained device | Validation-gated |
| L | Laptop / workstation | Reference candidate |
| S | Personal / private server | Reference candidate |
| E | Enterprise | Core local; federation deferred |
| G | Global ASF | End-state; implementation deferred |

Profiles change placement, not responsibility. The same architectural
invariants hold in every profile.
