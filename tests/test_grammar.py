import asyncio

from app.grammar import MasteryEngine, MeshConvergenceValidator


def test_mastery_engine():
    engine = MasteryEngine()
    engine.certify("node_phon_1")
    assert engine.is_mastered("node_phon_1")
    assert engine.subsystem_progress("Grammar", "Phonology") == 1.0

def test_convergence():
    validator = MeshConvergenceValidator(default_timeout=0.5)
    res = asyncio.run(validator.assert_converges(lambda: 1.0, 1.0, "test"))
    assert res.achieved_value == 1.0
