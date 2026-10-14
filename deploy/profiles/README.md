# deploy/profiles/

## What is here

Deployment profile definitions. One subdirectory per profile.

| Profile | Constraint |
|---|---|
| `departmental-cpu/` | Commodity CPU-only departmental deployment |
| `enterprise-multidepartment/` | Enterprise with tenant isolation |
| `device-continuity/` | Phone / laptop / server handoff |

## What belongs in a profile

Each profile directory should contain:

- `profile.json` — the profile definition
- A cross-reference to the components it includes
- Configuration overrides
- Resource assumptions

## What does not belong

Component definitions. A profile selects among existing components; it
does not define new ones. The profile changes placement, not ownership.
