import pytest
from dcs.core.difference_engine import ParallelDifferenceEngine

def test_engine_parallel_execution_pass():
    mock_processes = [
        {"id": 1, "command": ["echo", "PASS_1"]},
        {"id": 2, "command": ["echo", "PASS_2"]}
    ]
    engine = ParallelDifferenceEngine()
    results = engine.execute_parallel_audit(mock_processes)
    assert len(results) == 2
    assert all(r["status"] == "PASS" for r in results)
