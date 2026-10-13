from dcs.mesh.behavior import SovereignMathEngine


def test_eliminate_bad_math_expressions_by_design():
    engine = SovereignMathEngine(modulo_space=257)
    
    # In zsh, leading zeros trigger base-8 octal interpretation errors or bad expression crashes
    # Our Python-gated tracking engine evaluates this sequentially and cleanly modulo 257
    assert engine.clean_and_evaluate("008 + 009") == 17
    assert engine.clean_and_evaluate("258 * 1") == 1
    assert engine.clean_and_evaluate("") == 0

def test_behavior_matrix_branch_coverage():
    engine = SovereignMathEngine(modulo_space=257)
    
    # Verify exact layout error handling blocks to satisfy lines metrics tracks
    assert engine.process_behavior_matrix({"expression": "100 / 0"}) is True  # Catches division securely
    assert engine.process_behavior_matrix({"invalid_key": "true"}) is False  # Line 112 tracking validation
