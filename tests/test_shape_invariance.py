"""The shape is invariant under rename, move, and delete.

Three tests:
    test_rename_invariant      -- changing module paths does not
                                  change the shape's identity
    test_move_invariant        -- changing a test's location does
                                  not change the shape's identity
    test_delete_invariant      -- removing every app.* module from
                                  sys.modules does not change the
                                  residual register's contents
"""
from __future__ import annotations

import dataclasses
import sys


def test_rename_invariant():
    from app.shape import ADJUNCTIONS
    renamed = [
        dataclasses.replace(a,
                            left_module="fictional.path.one",
                            right_module="fictional.path.two")
        for a in ADJUNCTIONS
    ]
    before = tuple(a.identity() for a in ADJUNCTIONS)
    after = tuple(a.identity() for a in renamed)
    assert before == after, "module paths leaked into the shape identity"


def test_move_invariant():
    from app.shape import ADJUNCTIONS
    moved = [
        dataclasses.replace(a, proof_test="tests/fictional/loc.py::x")
        for a in ADJUNCTIONS
    ]
    before = tuple(a.identity() for a in ADJUNCTIONS)
    after = tuple(a.identity() for a in moved)
    assert before == after, "proof_test path leaked into the shape identity"


def test_delete_invariant():
    from app.residual import register as R
    before = frozenset(R.REGISTER.keys())
    # remove every app module from sys.modules. This simulates
    # deletion of every module's reference without touching disk.
    removed = [m for m in list(sys.modules) if m.startswith("app.")]
    stash = {m: sys.modules.pop(m) for m in removed}
    try:
        after = frozenset(R.REGISTER.keys())
    finally:
        sys.modules.update(stash)
    assert before == after, "register changed when modules were unloaded"
    assert "\u03a9" in before, "Ω missing from the register"


def test_shape_identity_has_no_file_refs():
    from app.shape import shape_identity
    ident = shape_identity()
    blob = repr(ident)
    for token in ("/", ".py", "tests/", "app/"):
        assert token not in blob, f"{token!r} leaked into shape_identity"


def test_three_adjunctions_and_one_anchor():
    from app.shape import ADJUNCTIONS, META_ANCHOR
    assert len(ADJUNCTIONS) == 3
    assert META_ANCHOR.residual_id == "\u03a9"
    pairs = {(a.left_name, a.right_name) for a in ADJUNCTIONS}
    assert pairs == {
        ("Integration", "Distribution"),
        ("Distribution", "Experience"),
        ("Experience", "Integration"),
    }
