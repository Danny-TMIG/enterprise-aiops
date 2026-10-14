import pytest
from src.public.service import CmpEvd003Service

def test_cmp_evd_003_service():
    svc = CmpEvd003Service()
    assert svc.component_id == "CMP-EVD-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
