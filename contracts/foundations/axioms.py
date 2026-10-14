"""ASF axioms — the assumptions the system is built on.

An axiom is a statement accepted without proof within the system. If an
axiom is false, the system's guarantees do not hold. Axioms are not
tested; they are declared. Any implementation that violates an axiom is
not an ASF implementation, regardless of what it does.
"""
from __future__ import annotations

from contracts.foundations.primitives import Identity, Layer


# ---------------------------------------------------------------- A1
AXIOM_1 = "No component may grant itself the authority owned by another."

def axiom_1(actor: Layer, claims_authority_of: Layer, action: str) -> bool:
    """A1: an actor at one layer cannot exercise another layer's authority."""
    if actor != claims_authority_of and action in ("authorize", "execute", "propose"):
        return False
    return True


# ---------------------------------------------------------------- A2
AXIOM_2 = "Authority is bounded, attributable, time-aware, and revocable."

def axiom_2(subject_id: str, action: str, object_id: str,
             valid_until: str, delegable: bool) -> bool:
    """A2: a grant names who, what, over what, until when, and whether it delegates."""
    return all(isinstance(v, str) and v for v in (subject_id, action, object_id, valid_until))


# ---------------------------------------------------------------- A3
AXIOM_3 = "Memory is not automatically truth."

def axiom_3(memory_class: str) -> bool:
    """A3: only governed facts carry verification; observations, preferences,
    inferences, and assertions do not."""
    return memory_class in {
        "observation", "user_preference", "inference", "assertion",
        "governed_fact", "memory", "model_state",
    }


# ---------------------------------------------------------------- A4
AXIOM_4 = "Schema validity does not establish truth, authorization, eligibility, or successful execution."

def axiom_4(schema_valid: bool, claimed_true: bool, claimed_authorized: bool,
            claimed_executed: bool) -> bool:
    """A4: passing schema does not entail any of the four."""
    if not schema_valid:
        return False
    return not (claimed_true or claimed_authorized or claimed_executed)


# ---------------------------------------------------------------- A5
AXIOM_5 = "Missing identity, authority, policy, classification, integrity, or evidence dependencies fail closed."

def axiom_5(dependencies: dict[str, bool]) -> bool:
    """A5: if any dependency is missing, the only permitted outcome is rejection."""
    required = ("identity", "authority", "policy", "classification", "integrity", "evidence")
    return all(dependencies.get(k, False) for k in required)


# ---------------------------------------------------------------- A6
AXIOM_6 = "Historical state and policy are corrected by supersession, not silent mutation."

def axiom_6(old_version: int, new_version: int, old_still_readable: bool) -> bool:
    """A6: a new version does not erase the old."""
    if new_version <= old_version:
        return False
    return old_still_readable


# ---------------------------------------------------------------- A7
AXIOM_7 = "Unvalidated mathematics or research mechanisms are never represented as implemented guarantees."

def axiom_7(maturity: str, claimed_as_guarantee: bool) -> bool:
    """A7: only M5 or M6 maturity may be claimed as an implemented guarantee."""
    if claimed_as_guarantee and maturity not in ("M5", "M6"):
        return False
    return True


ALL_AXIOMS = (
    AXIOM_1, AXIOM_2, AXIOM_3, AXIOM_4,
    AXIOM_5, AXIOM_6, AXIOM_7,
)
