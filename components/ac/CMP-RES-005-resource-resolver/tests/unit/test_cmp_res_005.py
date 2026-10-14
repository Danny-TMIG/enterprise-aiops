from src.public.service import CmpRes005Service


def test_cmp_res_005_service():
    svc = CmpRes005Service()
    assert svc.component_id == "CMP-RES-005"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
