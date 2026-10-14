"""
End-to-End Sovereign Integration Test
"""

from aiops_platform_metadusa_cell.engine import AIOpsEngine


def test_sovereign_cell_e2e():
    engine = AIOpsEngine()
    metrics = {"cpu_load": 14.2, "ram_usage": 42.1}
    count = engine.ingest(metrics)
    assert count == 1
    status = engine.status()
    assert status["buffered_metrics"] == 1
