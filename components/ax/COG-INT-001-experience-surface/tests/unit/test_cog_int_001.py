import pytest
from src.public.service import CogInt001Service

def test_cog_int_001_service():
    svc = CogInt001Service()
    assert svc.component_id == "COG-INT-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
