from src.public.service import CmpEvd001Service


def test_cmp_evd_001_service():
    svc = CmpEvd001Service()
    assert svc.component_id == "CMP-EVD-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
