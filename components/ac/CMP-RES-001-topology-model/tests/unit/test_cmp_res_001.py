from src.public.service import CmpRes001Service


def test_cmp_res_001_service():
    svc = CmpRes001Service()
    assert svc.component_id == "CMP-RES-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
