import pytest
from src.public.service import CmpTru001Service

def test_cmp_tru_001_service():
    svc = CmpTru001Service()
    assert svc.component_id == "CMP-TRU-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
