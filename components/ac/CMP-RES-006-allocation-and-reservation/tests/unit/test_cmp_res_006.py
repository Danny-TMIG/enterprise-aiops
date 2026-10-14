from src.public.service import CmpRes006Service


def test_cmp_res_006_service():
    svc = CmpRes006Service()
    assert svc.component_id == "CMP-RES-006"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
