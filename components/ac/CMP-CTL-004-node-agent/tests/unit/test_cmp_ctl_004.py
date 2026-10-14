import pytest
from src.public.service import CmpCtl004Service

def test_cmp_ctl_004_service():
    svc = CmpCtl004Service()
    assert svc.component_id == "CMP-CTL-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
