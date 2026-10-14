import pytest
from src.public.service import CmpDat002Service

def test_cmp_dat_002_service():
    svc = CmpDat002Service()
    assert svc.component_id == "CMP-DAT-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
