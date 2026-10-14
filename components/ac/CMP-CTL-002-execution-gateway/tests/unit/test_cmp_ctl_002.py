from src.public.service import CmpCtl002Service


def test_cmp_ctl_002_service():
    svc = CmpCtl002Service()
    assert svc.component_id == "CMP-CTL-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
