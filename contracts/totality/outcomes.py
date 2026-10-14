"""Totality of the decision outcome space.

Govern produces exactly five decision outcomes. Every decision resolves to
one of them. No sixth outcome exists. No decision is left unresolved.
"""
from __future__ import annotations

from contracts.foundations.primitives import Outcome


TERMINAL = {Outcome.ALLOW, Outcome.DENY}
NON_TERMINAL = {Outcome.CONDITIONAL, Outcome.ESCALATE}
INDETERMINATE = {Outcome.INDETERMINATE}


def is_terminal(o: Outcome) -> bool:
    """A terminal outcome closes the decision — no further resolution needed."""
    return o in TERMINAL


def is_deferred(o: Outcome) -> bool:
    """A deferred outcome needs further input before it becomes terminal."""
    return o in NON_TERMINAL


def is_fail_closed(o: Outcome) -> bool:
    """INDETERMINATE fails closed for consequential action."""
    return o in INDETERMINATE


def resolves_to_terminal(o: Outcome, followed_by: Outcome | None) -> bool:
    """A non-terminal outcome must eventually resolve to a terminal one."""
    if is_terminal(o):
        return True
    if followed_by is None:
        return False
    return is_terminal(followed_by)
