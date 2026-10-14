import pytest
from src.public.service import CmpRes003Service

def test_cmp_res_003_service():
    svc = CmpRes003Service()
    assert svc.component_id == "CMP-RES-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
