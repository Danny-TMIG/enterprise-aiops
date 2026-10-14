from aiops_platform.app.core.engine_patch import SovereignEnginePatch


def test_apply_and_history():
    eng = SovereignEnginePatch()
    assert eng.history() == []
    eng.apply("boot", {"stage": "test"})
    assert len(eng.history()) == 1


def test_merkle_root_is_stable():
    a = SovereignEnginePatch()
    a.apply("x", {"n": 1})
    b = SovereignEnginePatch()
    b.apply("x", {"n": 1})
    assert a.merkle_root() == b.merkle_root()


def test_merkle_root_changes():
    a = SovereignEnginePatch()
    a.apply("x", {"n": 1})
    b = SovereignEnginePatch()
    b.apply("x", {"n": 2})
    assert a.merkle_root() != b.merkle_root()
