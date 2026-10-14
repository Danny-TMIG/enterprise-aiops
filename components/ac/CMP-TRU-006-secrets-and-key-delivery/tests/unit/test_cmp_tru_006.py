import pytest
from src.public.service import CmpTru006Service

def test_cmp_tru_006_service():
    svc = CmpTru006Service()
    assert svc.component_id == "CMP-TRU-006"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
