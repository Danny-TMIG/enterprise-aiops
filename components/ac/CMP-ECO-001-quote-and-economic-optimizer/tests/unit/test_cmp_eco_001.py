import pytest
from src.public.service import CmpEco001Service

def test_cmp_eco_001_service():
    svc = CmpEco001Service()
    assert svc.component_id == "CMP-ECO-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
