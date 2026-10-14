import pytest
from src.public.service import CmpRes004Service

def test_cmp_res_004_service():
    svc = CmpRes004Service()
    assert svc.component_id == "CMP-RES-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
