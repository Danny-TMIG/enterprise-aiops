import pytest
from src.public.service import CmpTru004Service

def test_cmp_tru_004_service():
    svc = CmpTru004Service()
    assert svc.component_id == "CMP-TRU-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
