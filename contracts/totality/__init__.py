"""ASF totality — every category is exhaustive and mutually exclusive.

Layers of totality:

    actions    -- every action is assigned to exactly one layer
    objects    -- every boundary object is in exactly one category
    outcomes   -- every decision resolves to one of five outcomes
    failures   -- every failure is in exactly one class with one response
    lifecycle  -- every stage in the canonical lifecycle has one owner
    coverage   -- every component directory is classified

If any of these fails totality, the system has an unclassified case. An
unclassified case is a bug: the architecture does not know who owns it.
"""
from contracts.totality import actions, objects, outcomes, failures, lifecycle, coverage

__all__ = ["actions", "objects", "outcomes", "failures", "lifecycle", "coverage"]
