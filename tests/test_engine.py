import pytest
from aiops_platform_metadusa_cell.engine import AIOpsEngine

def test_engine_ingestion():
    engine = AIOpsEngine()
    count = engine.ingest({"cpu_load": 12.4, "ram_usage": 45.2})
    assert count == 1
    st = engine.status()
    assert st["buffered_metrics"] == 1
