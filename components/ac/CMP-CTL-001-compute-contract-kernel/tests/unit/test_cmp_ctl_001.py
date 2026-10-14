from src.public.service import CmpCtl001Service


def test_cmp_ctl_001_service():
    svc = CmpCtl001Service()
    assert svc.component_id == "CMP-CTL-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
