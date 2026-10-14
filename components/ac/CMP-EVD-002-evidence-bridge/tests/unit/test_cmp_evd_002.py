from src.public.service import CmpEvd002Service


def test_cmp_evd_002_service():
    svc = CmpEvd002Service()
    assert svc.component_id == "CMP-EVD-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
