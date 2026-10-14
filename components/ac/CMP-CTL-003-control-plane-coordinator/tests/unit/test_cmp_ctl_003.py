import pytest
from src.public.service import CmpCtl003Service

def test_cmp_ctl_003_service():
    svc = CmpCtl003Service()
    assert svc.component_id == "CMP-CTL-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
