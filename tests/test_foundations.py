"""Foundational properties: primitives, axioms, postulates, invariants, layer soundness."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from contracts.foundations import axioms, postulates, invariants, layers
from contracts.foundations.primitives import Layer, Outcome, Classification


# ---------------------------------------------------------------- primitives
def test_layer_is_exhaustive():
    assert {l.value for l in Layer} == {"cognition", "govern", "compute"}


def test_outcome_is_exhaustive():
    assert {o.value for o in Outcome} == {
        "allow", "deny", "conditional", "escalate", "indeterminate"
    }


def test_classification_is_ordered():
    order = [Classification.UNCLASSIFIED, Classification.INTERNAL,
             Classification.CONFIDENTIAL, Classification.SECRET]
    assert len(order) == 4
    assert order[0].value == "unclassified"
    assert order[-1].value == "secret"


# ---------------------------------------------------------------- axioms
def test_axiom_1_blocks_cross_layer_authority():
    assert not axioms.axiom_1(Layer.COGNITION, Layer.GOVERN, "authorize")
    assert axioms.axiom_1(Layer.GOVERN, Layer.GOVERN, "authorize")


def test_axiom_2_requires_all_fields():
    assert axioms.axiom_2("alice", "read", "doc-1", "2026-11-01T00:00:00Z", False)
    assert not axioms.axiom_2("", "read", "doc-1", "2026-11-01T00:00:00Z", False)


def test_axiom_3_memory_classes():
    for c in ("observation", "user_preference", "inference", "assertion", "governed_fact"):
        assert axioms.axiom_3(c)
    assert not axioms.axiom_3("something_else")


def test_axiom_4_schema_validity_entails_nothing():
    assert axioms.axiom_4(True, False, False, False)
    assert not axioms.axiom_4(True, True, False, False)
    assert not axioms.axiom_4(True, False, True, False)


def test_axiom_5_fail_closed_on_missing_dep():
    assert axioms.axiom_5({
        "identity": True, "authority": True, "policy": True,
        "classification": True, "integrity": True, "evidence": True,
    })
    assert not axioms.axiom_5({
        "identity": True, "authority": True, "policy": True,
        "classification": True, "integrity": False, "evidence": True,
    })


def test_axiom_6_supersession_not_mutation():
    assert axioms.axiom_6(1, 2, old_still_readable=True)
    assert not axioms.axiom_6(1, 2, old_still_readable=False)
    assert not axioms.axiom_6(2, 2, old_still_readable=True)


def test_axiom_7_research_not_guarantee():
    assert axioms.axiom_7("M2", claimed_as_guarantee=False)
    assert not axioms.axiom_7("M2", claimed_as_guarantee=True)
    assert axioms.axiom_7("M5", claimed_as_guarantee=True)


# ---------------------------------------------------------------- postulates
def test_all_postulates_are_open():
    opens = postulates.open_postulates()
    assert len(opens) == len(postulates.POSTULATES)


def test_postulate_ids_unique():
    ids = [p.id for p in postulates.POSTULATES]
    assert len(ids) == len(set(ids))


def test_postulate_status_vocabulary():
    allowed = {"open", "under_review", "proved", "refuted"}
    for p in postulates.POSTULATES:
        assert p.status in allowed


# ---------------------------------------------------------------- invariants
def test_invariant_ids_unique():
    ids = [i.id for i in invariants.INVARIANTS]
    assert len(ids) == len(set(ids))


def test_invariant_sources():
    sources = {i.source for i in invariants.INVARIANTS}
    assert sources == {"Govern FAS", "Compute FAS", "Cognition FAS", "All FAS"}


def test_lookup_by_id():
    assert invariants.by_id("GOV-INV-001") is not None
    assert invariants.by_id("nonexistent") is None


def test_govern_invariants_present():
    gov = invariants.by_source("Govern FAS")
    assert len(gov) == 10


def test_compute_invariants_present():
    cmp_ = invariants.by_source("Compute FAS")
    assert len(cmp_) == 12


def test_cognition_invariants_present():
    cog = invariants.by_source("Cognition FAS")
    assert len(cog) == 9


def test_cross_layer_invariants_present():
    env = invariants.by_source("All FAS")
    assert len(env) == 5


# ---------------------------------------------------------------- layer soundness
def test_separation():
    assert layers.separation(Layer.COGNITION, "propose")
    assert not layers.separation(Layer.COGNITION, "execute")
    assert layers.separation(Layer.GOVERN, "authorize")
    assert not layers.separation(Layer.GOVERN, "execute")
    assert layers.separation(Layer.COMPUTE, "execute")
    assert not layers.separation(Layer.COMPUTE, "authorize")


def test_totality():
    assert layers.totality([Layer.COGNITION, Layer.GOVERN, Layer.COMPUTE])
    assert not layers.totality([Layer.COGNITION, Layer.GOVERN])


def test_non_amplification():
    assert not layers.non_amplification(Layer.GOVERN, Layer.COMPUTE, "authorize")
    assert layers.non_amplification(Layer.GOVERN, Layer.COMPUTE, "realize")


def test_authority_conservation():
    assert layers.authority_conservation({"a", "b"}, {"a"})
    assert layers.authority_conservation({"a"}, {"a"})
    assert not layers.authority_conservation({"a"}, {"a", "b"})
