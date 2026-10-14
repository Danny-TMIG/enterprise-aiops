import pytest
from src.public.service import CmpRes002Service

def test_cmp_res_002_service():
    svc = CmpRes002Service()
    assert svc.component_id == "CMP-RES-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
