from src.public.service import CmpTru005Service


def test_cmp_tru_005_service():
    svc = CmpTru005Service()
    assert svc.component_id == "CMP-TRU-005"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
