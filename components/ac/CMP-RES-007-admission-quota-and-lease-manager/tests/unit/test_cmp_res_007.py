from src.public.service import CmpRes007Service


def test_cmp_res_007_service():
    svc = CmpRes007Service()
    assert svc.component_id == "CMP-RES-007"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
