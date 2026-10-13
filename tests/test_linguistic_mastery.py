
import pytest

from app.grammar.engine import MasteryEngine
from app.mesh.convergence import MeshConvergenceValidator


@pytest.mark.asyncio
async def test_linguistic_mastery_pipeline() -> None:
    engine = MasteryEngine()

    assert "Grammar" in engine.taxonomy
    subdomains = engine.taxonomy["Grammar"]

    expected_subdomains = [
        "Phonology", "Morphology", "Syntax",
        "Semantics", "Pragmatics", "Discourse", "Theoretical grammar"
    ]
    for sub in expected_subdomains:
        assert sub in subdomains
        assert len(subdomains[sub]) > 0

    validator = MeshConvergenceValidator(default_timeout=2.0, poll_interval=0.01)

    for sub, nodes in subdomains.items():
        for node in nodes:
            engine.certify(node)
            assert engine.is_mastered(node)
        
        metrics = await validator.assert_converges(
            probe_fn=lambda s=sub: engine.subsystem_progress("Grammar", s),
            expected=1.0,
            subsystem=f"LinguisticMesh-{sub}"
        )
        assert metrics.achieved_value == 1.0
