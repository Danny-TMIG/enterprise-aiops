"""Totality — every category is exhaustive and non-overlapping."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from contracts.totality import actions, objects, outcomes, failures, lifecycle, coverage
from contracts.foundations.primitives import Layer, Outcome


# ---------------------------------------------------------------- actions
def test_every_action_kind_is_assigned():
    assigned = {a.action for a in actions.ASSIGNMENTS}
    declared = set(actions.ActionKind)
    missing = declared - assigned
    assert not missing, f"unassigned actions: {missing}"


def test_no_stale_action_assignments():
    declared = set(actions.ActionKind)
    for a in actions.ASSIGNMENTS:
        assert a.action in declared, f"stale assignment: {a.action}"


def test_every_action_has_exactly_one_owner():
    seen = {}
    for a in actions.ASSIGNMENTS:
        assert a.action not in seen, f"duplicate assignment: {a.action}"
        seen[a.action] = a.owner


def test_all_three_layers_own_actions():
    owners = {a.owner for a in actions.ASSIGNMENTS}
    assert Layer.COGNITION in owners
    assert Layer.GOVERN in owners
    assert Layer.COMPUTE in owners


def test_cross_layer_actions_owned_by_govern():
    for action in (actions.ActionKind.ABSTAIN, actions.ActionKind.FAIL,
                   actions.ActionKind.DEGRADE, actions.ActionKind.CONTAIN):
        assert actions.owner_of(action) == Layer.GOVERN


# ---------------------------------------------------------------- objects
def test_all_objects_have_known_category():
    for o in objects.OBJECTS:
        assert o.category in objects.CATEGORIES, f"unknown category: {o.category}"


def test_common_envelope_is_in_envelope_category():
    assert objects.categories_of("CommonEnvelope") == ["envelope"]


def test_every_category_is_populated():
    for cat in objects.CATEGORIES:
        assert objects.in_category(cat), f"empty category: {cat}"


def test_object_names_unique():
    names = [o.name for o in objects.OBJECTS]
    assert len(names) == len(set(names))


# ---------------------------------------------------------------- outcomes
def test_outcome_partition():
    all_outcomes = set(Outcome)
    terminal = outcomes.TERMINAL
    nonterminal = outcomes.NON_TERMINAL
    indeterminate = outcomes.INDETERMINATE
    assert terminal | nonterminal | indeterminate == all_outcomes
    assert not (terminal & nonterminal)
    assert not (terminal & indeterminate)
    assert not (nonterminal & indeterminate)


def test_terminal_outcomes():
    assert outcomes.is_terminal(Outcome.ALLOW)
    assert outcomes.is_terminal(Outcome.DENY)
    assert not outcomes.is_terminal(Outcome.CONDITIONAL)


def test_indeterminate_fails_closed():
    assert outcomes.is_fail_closed(Outcome.INDETERMINATE)


def test_nonterminal_resolves_to_terminal():
    assert outcomes.resolves_to_terminal(Outcome.CONDITIONAL, Outcome.ALLOW)
    assert outcomes.resolves_to_terminal(Outcome.ESCALATE, Outcome.DENY)
    assert not outcomes.resolves_to_terminal(Outcome.CONDITIONAL, None)


# ---------------------------------------------------------------- failures
def test_every_failure_class_has_response():
    for cls in failures.CLASSES:
        assert cls.required_response
        assert cls.examples


def test_all_examples_are_classified():
    for example in failures.all_examples():
        assert failures.classify(example) is not None


def test_every_class_has_examples():
    for cls in failures.CLASSES:
        assert len(cls.examples) >= 3, f"class {cls.name} has too few examples"


def test_unclassified_example_returns_none():
    assert failures.classify("something completely unknown") is None


# ---------------------------------------------------------------- lifecycle
def test_governed_lifecycle_is_contiguous():
    assert lifecycle.stages_are_contiguous(lifecycle.GOVERNED_STAGES)


def test_cognitive_lifecycle_is_contiguous():
    assert lifecycle.stages_are_contiguous(lifecycle.COGNITIVE_STAGES)


def test_execution_lifecycle_is_contiguous():
    assert lifecycle.stages_are_contiguous(lifecycle.EXECUTION_STEPS)


def test_every_stage_has_owner():
    for stages in (lifecycle.GOVERNED_STAGES, lifecycle.COGNITIVE_STAGES,
                   lifecycle.EXECUTION_STEPS):
        assert lifecycle.every_stage_has_owner(stages)


# ---------------------------------------------------------------- coverage
def test_all_component_dirs_are_classified():
    dirs = coverage.classify_dirs(ROOT)
    assert dirs, "no component dirs found"
    for d in dirs:
        assert d.classification in set(coverage.DirClass)


def test_no_orphan_directories():
    dirs = coverage.classify_dirs(ROOT)
    orphans = [d for d in dirs if d.classification == coverage.DirClass.ORPHAN]
    assert not orphans, f"orphan dirs: {[d.path for d in orphans]}"


def test_coverage_summary_counts_all_dirs():
    dirs = coverage.classify_dirs(ROOT)
    counts = coverage.summary(dirs)
    assert sum(counts.values()) == len(dirs)


def test_logical_and_alias_are_balanced():
    dirs = coverage.classify_dirs(ROOT)
    counts = coverage.summary(dirs)
    logical = counts[coverage.DirClass.LOGICAL]
    alias = counts[coverage.DirClass.ALIAS]
    assert logical == alias, (
        f"unbalanced: {logical} logical vs {alias} alias dirs"
    )
